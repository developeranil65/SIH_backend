-- CreateTable
CREATE TABLE "public"."HospitalRecord" (
    "id" SERIAL NOT NULL,
    "patientId" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "hospitalId" TEXT,
    "doctorId" TEXT,
    "reportedBy" TEXT,
    "age" INTEGER,
    "gender" TEXT,
    "symptoms" TEXT,
    "diagnosis" TEXT,
    "severity" TEXT,
    "outcome" TEXT,
    "visitDate" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "HospitalRecord_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."PharmaSale" (
    "id" SERIAL NOT NULL,
    "pharmacyId" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "pharmacyType" TEXT,
    "medicine" TEXT NOT NULL,
    "diseaseTarget" TEXT,
    "qtySold" INTEGER NOT NULL,
    "price" DOUBLE PRECISION NOT NULL,
    "saleDate" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PharmaSale_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."SocialPost" (
    "id" SERIAL NOT NULL,
    "postId" TEXT NOT NULL,
    "district" TEXT NOT NULL,
    "platform" TEXT NOT NULL,
    "content" TEXT NOT NULL,
    "sentiment" TEXT,
    "reach" TEXT,
    "timeStamp" TIMESTAMP(3) NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "SocialPost_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "public"."AggregatedSummary" (
    "id" SERIAL NOT NULL,
    "district" TEXT NOT NULL,
    "date" TIMESTAMP(3) NOT NULL,
    "hospitalCaseCount" INTEGER NOT NULL,
    "severeCaseCount" INTEGER NOT NULL,
    "pharmaSalesCount" INTEGER NOT NULL,
    "socialPostsCount" INTEGER NOT NULL,
    "negativePostsCount" INTEGER NOT NULL,
    "outbreakRiskScore" DOUBLE PRECISION NOT NULL,
    "alertLevel" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AggregatedSummary_pkey" PRIMARY KEY ("id")
);
