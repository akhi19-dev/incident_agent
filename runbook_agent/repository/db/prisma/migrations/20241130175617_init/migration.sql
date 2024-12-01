-- CreateTable
CREATE TABLE "automation_script_documents" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "name" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "published_time" TIMESTAMP(3) NOT NULL,
    "is_indexed" BOOLEAN NOT NULL,
    "description" TEXT,
    "os_supported" TEXT[],
    "args" TEXT[],
    "created_time" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_time" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "type" TEXT NOT NULL,
    "tags" TEXT[],

    CONSTRAINT "automation_script_documents_pkey" PRIMARY KEY ("id")
);
