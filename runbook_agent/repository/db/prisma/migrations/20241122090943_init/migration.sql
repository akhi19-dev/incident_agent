-- CreateEnum
CREATE TYPE "IntegrationType" AS ENUM ('AZURE', 'PROMETHEUS', 'AWS', 'SERVICENOW');

-- CreateTable
CREATE TABLE "Event" (
    "id" TEXT NOT NULL,
    "org_id" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "manager" TEXT NOT NULL,
    "metric_type" TEXT NOT NULL,
    "severity" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "hostname" TEXT NOT NULL,
    "service" TEXT NOT NULL,
    "tags" JSONB,
    "additional_info" TEXT,
    "correlation_key" TEXT,
    "occurrence_count" INTEGER NOT NULL DEFAULT 1,
    "first_occurrence_time" TIMESTAMPTZ,
    "last_occurrence_time" TIMESTAMPTZ,

    CONSTRAINT "Event_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Incident" (
    "id" TEXT NOT NULL,
    "org_id" TEXT NOT NULL,
    "subject" TEXT NOT NULL,
    "start_time" TIMESTAMPTZ NOT NULL,
    "end_time" TIMESTAMPTZ NOT NULL,
    "severity" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "additional_info" JSONB,
    "urgency" INTEGER NOT NULL,
    "impact" INTEGER NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL,
    "url" TEXT,
    "runbooks" JSONB,

    CONSTRAINT "Incident_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Alert" (
    "id" TEXT NOT NULL,
    "org_id" TEXT NOT NULL,
    "subject" TEXT NOT NULL,
    "description" TEXT NOT NULL,
    "severity" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "start_time" TIMESTAMPTZ NOT NULL,
    "end_time" TIMESTAMPTZ,

    CONSTRAINT "Alert_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Metric" (
    "id" TEXT NOT NULL,
    "metric_type" TEXT NOT NULL,
    "org_id" TEXT NOT NULL,
    "created_at" TIMESTAMPTZ NOT NULL,
    "value" DOUBLE PRECISION NOT NULL,
    "hostname" TEXT NOT NULL,
    "tags" JSONB,

    CONSTRAINT "Metric_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Runbook" (
    "id" TEXT NOT NULL,
    "runbook_name" TEXT NOT NULL,
    "org_id" TEXT NOT NULL,
    "incident_id" TEXT NOT NULL,
    "job_name" TEXT NOT NULL,
    "status" TEXT NOT NULL,
    "timestamp" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "Runbook_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Integration" (
    "id" TEXT NOT NULL,
    "org_id" TEXT NOT NULL,
    "integration_type" "IntegrationType" NOT NULL,
    "integration_config" JSONB NOT NULL,
    "created_at" TIMESTAMPTZ(6) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ(6) NOT NULL,

    CONSTRAINT "Integration_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "automation_runbook_documents" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "org_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "source" TEXT NOT NULL,
    "publishedTime" TIMESTAMP(3) NOT NULL,
    "isIndexed" BOOLEAN NOT NULL,
    "description" TEXT NOT NULL,
    "osSupported" TEXT[],
    "args" TEXT[],
    "createdTime" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedTime" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "runbookType" TEXT NOT NULL,
    "tags" TEXT[],

    CONSTRAINT "automation_runbook_documents_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "_EventToIncident" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "_AlertToEvent" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateTable
CREATE TABLE "_AlertToIncident" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL
);

-- CreateIndex
CREATE UNIQUE INDEX "Runbook_job_name_key" ON "Runbook"("job_name");

-- CreateIndex
CREATE UNIQUE INDEX "_EventToIncident_AB_unique" ON "_EventToIncident"("A", "B");

-- CreateIndex
CREATE INDEX "_EventToIncident_B_index" ON "_EventToIncident"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_AlertToEvent_AB_unique" ON "_AlertToEvent"("A", "B");

-- CreateIndex
CREATE INDEX "_AlertToEvent_B_index" ON "_AlertToEvent"("B");

-- CreateIndex
CREATE UNIQUE INDEX "_AlertToIncident_AB_unique" ON "_AlertToIncident"("A", "B");

-- CreateIndex
CREATE INDEX "_AlertToIncident_B_index" ON "_AlertToIncident"("B");

-- AddForeignKey
ALTER TABLE "_EventToIncident" ADD CONSTRAINT "_EventToIncident_A_fkey" FOREIGN KEY ("A") REFERENCES "Event"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_EventToIncident" ADD CONSTRAINT "_EventToIncident_B_fkey" FOREIGN KEY ("B") REFERENCES "Incident"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_AlertToEvent" ADD CONSTRAINT "_AlertToEvent_A_fkey" FOREIGN KEY ("A") REFERENCES "Alert"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_AlertToEvent" ADD CONSTRAINT "_AlertToEvent_B_fkey" FOREIGN KEY ("B") REFERENCES "Event"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_AlertToIncident" ADD CONSTRAINT "_AlertToIncident_A_fkey" FOREIGN KEY ("A") REFERENCES "Alert"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "_AlertToIncident" ADD CONSTRAINT "_AlertToIncident_B_fkey" FOREIGN KEY ("B") REFERENCES "Incident"("id") ON DELETE CASCADE ON UPDATE CASCADE;
