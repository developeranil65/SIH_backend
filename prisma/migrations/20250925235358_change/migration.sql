/*
  Warnings:

  - You are about to drop the column `diseaseTarget` on the `PharmaSale` table. All the data in the column will be lost.
  - Added the required column `diagnosis` to the `AggregatedSummary` table without a default value. This is not possible if the table is not empty.

*/
-- AlterTable
ALTER TABLE "public"."AggregatedSummary" ADD COLUMN     "diagnosis" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "public"."PharmaSale" DROP COLUMN "diseaseTarget",
ADD COLUMN     "diagnosis" TEXT;
