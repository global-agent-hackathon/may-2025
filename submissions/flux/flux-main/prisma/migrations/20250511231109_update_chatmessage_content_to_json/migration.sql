/*
  Warnings:

  - Changed the type of `content` on the `ChatMessage` table. No cast exists, the column would be dropped and recreated, which cannot be done if there is data, since the column is required.

*/
-- AlterTable
-- Change the type of "content" on the "ChatMessage" table from TEXT to JSONB,
-- attempting to cast existing string content into a structured JSON object.
ALTER TABLE "ChatMessage"
ALTER COLUMN "content" DROP DEFAULT, -- If there was a default on the text column, drop it
ALTER COLUMN "content" TYPE JSONB
USING jsonb_build_object('type', 'text', 'data', "content"); -- Cast existing text

-- If the column was NOT NULL before, and you want it to remain NOT NULL as JSONB:
-- (The schema change to Json implies it can be null if not explicitly Json! - but our schema has it as required `Json` without `?`)
-- The `ADD COLUMN` from Prisma's attempt was `JSONB NOT NULL`.
-- If `jsonb_build_object` can somehow produce NULL (it shouldn't if "content" was NOT NULL text),
-- you might need to handle that or ensure the column remains NOT NULL if that was intended.
-- For now, assuming `jsonb_build_object` with a text input will always produce a valid JSONB object.
