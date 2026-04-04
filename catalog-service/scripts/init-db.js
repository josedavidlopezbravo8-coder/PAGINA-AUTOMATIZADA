require('dotenv').config();
const { Client } = require('pg');

async function ensureDatabase() {
  const defaultConnectionString = process.env.DATABASE_URL || 'postgres://postgres:postgres@localhost:5432/catalog';
  const url = new URL(defaultConnectionString);
  const databaseName = url.pathname.replace('/', '') || 'catalog';

  // Connect to default postgres db (or maintainers can set PGDATABASE to a different default)
  const adminDb = new URL(defaultConnectionString);
  adminDb.pathname = '/postgres';

  const client = new Client({ connectionString: adminDb.toString() });
  await client.connect();

  try {
    const exists = await client.query('SELECT 1 FROM pg_database WHERE datname = $1', [databaseName]);
    if (exists.rowCount === 0) {
      console.log(`Creating database ${databaseName} ...`);
      await client.query(`CREATE DATABASE ${databaseName}`);
      console.log('Database created.');
    } else {
      console.log(`Database ${databaseName} already exists.`);
    }
  } finally {
    await client.end();
  }
}

ensureDatabase().catch((err) => {
  console.error('Failed to ensure database exists:', err);
  process.exit(1);
});
