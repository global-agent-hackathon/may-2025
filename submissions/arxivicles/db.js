import pg from 'pg';
import dotenv from 'dotenv';

dotenv.config();

const { Pool } = pg;

const pool = new Pool({
    connectionString: process.env.DATABASE_URL
});

// Initialize database tables
export const initDatabase = async () => {
    try {
        await pool.query(`
            CREATE TABLE IF NOT EXISTS subscribers (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_sent_at TIMESTAMP
            );
        `);
        console.log('Database initialized successfully');
    } catch (error) {
        console.error('Error initializing database:', error);
        throw error;
    }
};

// Add a new subscriber
export const addSubscriber = async (email) => {
    try {
        const result = await pool.query(
            'INSERT INTO subscribers (email) VALUES ($1) ON CONFLICT (email) DO NOTHING RETURNING *',
            [email]
        );
        return result.rows[0];
    } catch (error) {
        console.error('Error adding subscriber:', error);
        throw error;
    }
};

// Get all subscribers
export const getSubscribers = async () => {
    try {
        const result = await pool.query('SELECT * FROM subscribers');
        return result.rows;
    } catch (error) {
        console.error('Error getting subscribers:', error);
        throw error;
    }
};

// Update last sent timestamp for a subscriber
export const updateLastSent = async (email) => {
    try {
        await pool.query(
            'UPDATE subscribers SET last_sent_at = CURRENT_TIMESTAMP WHERE email = $1',
            [email]
        );
    } catch (error) {
        console.error('Error updating last sent timestamp:', error);
        throw error;
    }
};

// Remove a subscriber
export const removeSubscriber = async (email) => {
    try {
        await pool.query('DELETE FROM subscribers WHERE email = $1', [email]);
    } catch (error) {
        console.error('Error removing subscriber:', error);
        throw error;
    }
}; 