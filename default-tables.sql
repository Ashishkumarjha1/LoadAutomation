-- MariaDB dump 10.18  Distrib 10.5.8-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: test6
-- ------------------------------------------------------
-- Server version	10.5.8-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES UTF8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alerts`
--

DROP TABLE IF EXISTS `alerts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alerts` (
  `TimeStamp` timestamp NOT NULL,
  `RelativeTime` varchar(50) NOT NULL,
  `CameraName` varchar(255) NOT NULL,
  `Feature` varchar(255) NOT NULL,
  `ObjectType` varchar(50) NOT NULL,
  `BoundingBox` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alerts`
--

LOCK TABLES `alerts` WRITE;
/*!40000 ALTER TABLE `alerts` DISABLE KEYS */;
/*!40000 ALTER TABLE `alerts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `camerainfo`
--

DROP TABLE IF EXISTS `camerainfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `camerainfo` (
  `TimeStamp` timestamp NOT NULL,
  `RelativeTime` varchar(50) NOT NULL,
  `CameraName` varchar(255) NOT NULL,
  `InputFPS` float NOT NULL,
  `OutputFPS` float NOT NULL,
  `EnqueuedFrames` int(11) NOT NULL,
  `DecodedFrames` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `camerainfo`
--

LOCK TABLES `camerainfo` WRITE;
/*!40000 ALTER TABLE `camerainfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `camerainfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cpumemoryusage`
--

DROP TABLE IF EXISTS `cpumemoryusage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cpumemoryusage` (
  `TimeStamp` timestamp NOT NULL,
  `RelativeTime` varchar(50) DEFAULT NULL,
  `ServerIP` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='All dockers memory usage info';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cpumemoryusage`
--

LOCK TABLES `cpumemoryusage` WRITE;
/*!40000 ALTER TABLE `cpumemoryusage` DISABLE KEYS */;
/*!40000 ALTER TABLE `cpumemoryusage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cpuusage`
--

DROP TABLE IF EXISTS `cpuusage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cpuusage` (
  `TimeStamp` timestamp NOT NULL,
  `RelativeTime` varchar(50) DEFAULT NULL,
  `ServerIP` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='All dockers CPU usage info';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cpuusage`
--

LOCK TABLES `cpuusage` WRITE;
/*!40000 ALTER TABLE `cpuusage` DISABLE KEYS */;
/*!40000 ALTER TABLE `cpuusage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `gpustats`
--

DROP TABLE IF EXISTS `gpustats`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `gpustats` (
  `TimeStamp` timestamp NOT NULL,
  `RelativeTime` varchar(50) DEFAULT NULL,
  `ServerIP` varchar(50) DEFAULT NULL,
  `GraphicsCurrClock` varchar(50) DEFAULT NULL,
  `CurrentTemp` varchar(50) DEFAULT NULL,
  `CurrentPowerUsage` varchar(50) DEFAULT NULL,
  `GPUUsagePerc` varchar(50) DEFAULT NULL,
  `GPUMemory` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='GPU clock, temperature, power and usage info';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gpustats`
--

LOCK TABLES `gpustats` WRITE;
/*!40000 ALTER TABLE `gpustats` DISABLE KEYS */;
/*!40000 ALTER TABLE `gpustats` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `decoderserviceinfo`
--

DROP TABLE IF EXISTS `decoderserviceinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `decoderserviceinfo` (
	`TimeStamp` timestamp NOT NULL,
	`PktCount` varchar(50) DEFAULT NULL,
	`CameraName` varchar(50) DEFAULT NULL,
	`HardwareType` varchar(50) DEFAULT NULL,
	`AvgDecodeTime` varchar(50) DEFAULT NULL,
	`AvgDecodeFPS` varchar(50) DEFAULT NULL
)ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci COMMENT='Decoder service logs info';
/*!40101 SET character_set_client = @saved_cs_client */;


--
-- Dumping data for table `decoderserviceinfo`
--

LOCK TABLES `decoderserviceinfo` WRITE;
/*!40000 ALTER TABLE `decoderserviceinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `decoderserviceinfo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `serverinfo`
--

DROP TABLE IF EXISTS `serverinfo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `serverinfo` (
  `ServerIP` varchar(50) DEFAULT NULL,
  `GraphicsMaxClock` varchar(50) DEFAULT NULL,
  `ShutdownTemp` varchar(50) DEFAULT NULL,
  `SlowdownTemp` varchar(50) DEFAULT NULL,
  `MaxOperatingTemp` varchar(50) DEFAULT NULL,
  `GPUMaxPower` varchar(50) DEFAULT NULL,
  `Storagestatus` int(11) DEFAULT NULL,
  `CPUCores` varchar(50) DEFAULT NULL,
  `RAM` varchar(50) DEFAULT NULL,
  `GPUName` varchar(50) DEFAULT NULL,
  `ModelName` varchar(50) DEFAULT NULL,
  `Features` varchar(1000) DEFAULT NULL,
  `TargetFPS` varchar(50) DEFAULT NULL,
  `TimeStamp` timestamp NULL DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='Server Info';
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `serverinfo`
--

LOCK TABLES `serverinfo` WRITE;
/*!40000 ALTER TABLE `serverinfo` DISABLE KEYS */;
/*!40000 ALTER TABLE `serverinfo` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-05-04  6:50:49