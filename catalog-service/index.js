require('dotenv').config();
const express = require('express');
const { Pool } = require('pg');

const app = express();
app.use(express.json());

const pool = new Pool({
  connectionString: process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/catalog',
});

const runMigrations = async () => {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS categories (
      id SERIAL PRIMARY KEY,
      name VARCHAR(255) NOT NULL UNIQUE,
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS books (
      id SERIAL PRIMARY KEY,
      title VARCHAR(1024) NOT NULL,
      author VARCHAR(1024) NOT NULL,
      category_id INTEGER REFERENCES categories(id) ON DELETE SET NULL,
      isbn VARCHAR(32),
      issn VARCHAR(32),
      created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
      updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
  `);
};

app.post('/books', async (req, res) => {
  const { title, author, category, isbn, issn } = req.body;

  if (!title || !author) {
    return res.status(400).json({
      error: 'title and author are required',
    });
  }

  const client = await pool.connect();

  try {
    await client.query('BEGIN');

    let categoryId = null;
    if (category) {
      const categoryResult = await client.query(
        'INSERT INTO categories(name) VALUES($1) ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name RETURNING id',
        [category]
      );
      categoryId = categoryResult.rows[0].id;
    }

    const bookResult = await client.query(
      `INSERT INTO books (title, author, category_id, isbn, issn)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [title, author, categoryId, isbn || null, issn || null]
    );

    await client.query('COMMIT');

    const book = bookResult.rows[0];

    const response = {
      id: book.id,
      title: book.title,
      author: book.author,
      isbn: book.isbn,
      issn: book.issn,
      created_at: book.created_at,
      updated_at: book.updated_at,
      category: category ? category : null,
    };

    res.status(201).json(response);
  } catch (error) {
    await client.query('ROLLBACK');
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  } finally {
    client.release();
  }
});

app.get('/books', async (req, res) => {
  const page = Math.max(Number(req.query.page) || 1, 1);
  const limit = Math.min(Math.max(Number(req.query.limit) || 10, 1), 100);
  const offset = (page - 1) * limit;

  const q = (req.query.q || '').trim();
  const category = (req.query.category || '').trim();

  const filters = [];
  const params = [];

  if (q) {
    params.push(`%${q.toLowerCase()}%`);
    params.push(`%${q.toLowerCase()}%`);
    filters.push(`(LOWER(b.title) LIKE $${params.length - 1} OR LOWER(b.author) LIKE $${params.length})`);
  }

  if (category) {
    params.push(category);
    filters.push(`c.name = $${params.length}`);
  }

  let whereClause = '';
  if (filters.length > 0) {
    whereClause = `WHERE ${filters.join(' AND ')}`;
  }

  try {
    const totalSql = `
      SELECT COUNT(*)::int AS total
      FROM books b
      LEFT JOIN categories c ON b.category_id = c.id
      ${whereClause}
    `;

    const totalResult = await pool.query(totalSql, params);
    const totalCount = totalResult.rows[0].total;

    const dataSql = `
      SELECT b.id, b.title, b.author, b.isbn, b.issn, b.created_at, b.updated_at,
             c.id AS category_id, c.name AS category_name
      FROM books b
      LEFT JOIN categories c ON b.category_id = c.id
      ${whereClause}
      ORDER BY b.id ASC
      LIMIT $${params.length + 1} OFFSET $${params.length + 2}
    `;

    const dataParams = [...params, limit, offset];
    const result = await pool.query(dataSql, dataParams);

    const books = result.rows.map((row) => ({
      id: row.id,
      title: row.title,
      author: row.author,
      isbn: row.isbn,
      issn: row.issn,
      category: row.category_id ? { id: row.category_id, name: row.category_name } : null,
      created_at: row.created_at,
      updated_at: row.updated_at,
    }));

    res.json({
      page,
      limit,
      total: totalCount,
      results: books,
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.get('/books/count', async (req, res) => {
  try {
    const result = await pool.query('SELECT COUNT(*)::int AS total FROM books');
    res.json({ total: result.rows[0].total });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.get('/books/:id', async (req, res) => {
  const id = Number(req.params.id);
  if (!Number.isInteger(id) || id <= 0) {
    return res.status(400).json({ error: 'invalid book id' });
  }

  try {
    const result = await pool.query(
      `SELECT b.id, b.title, b.author, b.isbn, b.issn, b.created_at, b.updated_at,
              c.id AS category_id, c.name AS category_name
       FROM books b
       LEFT JOIN categories c ON b.category_id = c.id
       WHERE b.id = $1`,
      [id]
    );

    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'book not found' });
    }

    const row = result.rows[0];
    res.json({
      id: row.id,
      title: row.title,
      author: row.author,
      isbn: row.isbn,
      issn: row.issn,
      category: row.category_id ? { id: row.category_id, name: row.category_name } : null,
      created_at: row.created_at,
      updated_at: row.updated_at,
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.get('/books/genres/minimum', async (req, res) => {
  const minCount = Number(req.query.min || 2);
  if (!Number.isInteger(minCount) || minCount < 1) {
    return res.status(400).json({ error: 'min must be a positive integer' });
  }

  try {
    const result = await pool.query(
      `SELECT c.id, c.name, COUNT(b.id) AS book_count
       FROM categories c
       LEFT JOIN books b ON b.category_id = c.id
       GROUP BY c.id, c.name
       HAVING COUNT(b.id) >= $1
       ORDER BY c.name ASC`,
      [minCount]
    );

    const booksByGenre = result.rows.map((row) => ({
      id: row.id,
      name: row.name,
      book_count: Number(row.book_count),
    }));

    res.json(booksByGenre);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.get('/books/genres/count', async (req, res) => {
  try {
    const result = await pool.query(
      `SELECT c.id, c.name, COUNT(b.id) AS book_count
       FROM categories c
       LEFT JOIN books b ON b.category_id = c.id
       GROUP BY c.id, c.name
       ORDER BY c.name ASC`
    );

    const booksByGenre = result.rows.map((row) => ({
      id: row.id,
      name: row.name,
      book_count: Number(row.book_count),
    }));

    res.json(booksByGenre);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.get('/categories', async (req, res) => {
  try {
    const result = await pool.query('SELECT id, name, created_at, updated_at FROM categories ORDER BY name');
    res.json(result.rows);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.post('/categories', async (req, res) => {
  const { name } = req.body;
  if (!name) {
    return res.status(400).json({ error: 'name required' });
  }

  try {
    const result = await pool.query(
      'INSERT INTO categories(name) VALUES ($1) ON CONFLICT (name) DO UPDATE SET updated_at = NOW() RETURNING *',
      [name]
    );
    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'internal server error' });
  }
});

app.use((req, res) => {
  res.status(404).json({ error: 'not found' });
});

const port = Number(process.env.PORT) || 3000;

runMigrations()
  .then(() => {
    app.listen(port, () => {
      console.log(`Catalog service listening on port ${port}`);
    });
  })
  .catch((err) => {
    console.error('Failed to start app:', err);
    process.exit(1);
  });
