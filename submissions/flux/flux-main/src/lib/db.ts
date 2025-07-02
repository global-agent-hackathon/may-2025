import { PrismaClient } from '@prisma/client'

// PrismaClient is attached to the `global` object in development to prevent
// exhausting your database connection limit.
// Learn more: https://pris.ly/d/help/next-js-best-practices

const globalForPrisma = global as unknown as { prisma: PrismaClient }

// Create a singleton Prisma Client
export const prisma =
  globalForPrisma.prisma ||
  new PrismaClient({
    log: process.env.NODE_ENV === "development" ? ["error", "warn"] : ["error"],
    // Add connection management options to prevent random disconnects
    datasources: {
      db: {
        url: process.env.DATABASE_URL,
      },
    },
  })

// Handle connection errors
process.on("unhandledRejection", (reason) => {
  console.error("Unhandled Rejection at:", reason)
  // Prevent process crash on connection errors
})

if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = prisma

export default prisma 