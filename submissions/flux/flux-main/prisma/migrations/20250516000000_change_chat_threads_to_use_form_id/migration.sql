-- Migration to change ChatThread from formResponseId to formId
-- Delete existing chat data first to avoid migration complexity

-- Step 1: Delete all existing chat messages and threads
DELETE FROM "ChatMessage" WHERE EXISTS (SELECT 1 FROM "ChatThread" WHERE "ChatThread"."id" = "ChatMessage"."threadId");
DELETE FROM "ChatThread";

-- Step 2: Drop the old foreign key constraint if it exists
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ChatThread_formResponseId_fkey') THEN
        ALTER TABLE "ChatThread" DROP CONSTRAINT "ChatThread_formResponseId_fkey";
    END IF;
END $$;

-- Step 3: Drop the old formResponseId column if it exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'ChatThread' AND column_name = 'formResponseId') THEN
        ALTER TABLE "ChatThread" DROP COLUMN "formResponseId";
    END IF;
END $$;

-- Step 4: Add the new formId column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'ChatThread' AND column_name = 'formId') THEN
        ALTER TABLE "ChatThread" ADD COLUMN "formId" TEXT NOT NULL DEFAULT '';
        -- Remove default after adding
        ALTER TABLE "ChatThread" ALTER COLUMN "formId" DROP DEFAULT;
    END IF;
END $$;

-- Step 5: Add the new foreign key constraint if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ChatThread_formId_fkey') THEN
        ALTER TABLE "ChatThread" ADD CONSTRAINT "ChatThread_formId_fkey" FOREIGN KEY ("formId") REFERENCES "Form"("id") ON DELETE CASCADE ON UPDATE CASCADE;
    END IF;
END $$; 