/*
  Warnings:

  - You are about to drop the column `runbooks` on the `Incident` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Incident" DROP COLUMN "runbooks",
ADD COLUMN     "runbook_executed" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "runbook_link" TEXT,
ADD COLUMN     "runbook_name" TEXT,
ADD COLUMN     "runbook_output" TEXT,
ADD COLUMN     "runbook_status" TEXT;

-- CreateTable
CREATE TABLE "incident_management" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "zenoss_incidentmanagement_number" TEXT NOT NULL,
    "event_state" TEXT NOT NULL,
    "severity" INTEGER NOT NULL,
    "device" TEXT NOT NULL,
    "component" TEXT NOT NULL,
    "event_class" TEXT NOT NULL,
    "summary" TEXT NOT NULL,
    "first_time" TIMESTAMP(3) NOT NULL,
    "last_time" TIMESTAMP(3) NOT NULL,
    "count" INTEGER NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL,

    CONSTRAINT "incident_management_pkey" PRIMARY KEY ("id")
);
