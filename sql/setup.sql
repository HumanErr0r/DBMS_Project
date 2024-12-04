-- users
CREATE TABLE `users` (
  `UserID` int NOT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `LastName` varchar(45) DEFAULT NULL,
  `Email` varchar(45) DEFAULT NULL,
  `PhoneNumber` varchar(45) DEFAULT NULL,
  `Password` varchar(100) DEFAULT NULL,
  `Gender` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`UserID`),
  UNIQUE KEY `UserID_UNIQUE` (`UserID`),
  UNIQUE KEY `Email_UNIQUE` (`Email`)
);

-- admin
CREATE TABLE `admins` (
  `AdminID` int NOT NULL,
  `FirstName` varchar(45) DEFAULT NULL,
  `LastName` varchar(45) DEFAULT NULL,
  `Email` varchar(45) DEFAULT NULL,
  `PhoneNumber` varchar(45) DEFAULT NULL,
  `Password` varchar(100) DEFAULT NULL,
  `Gender` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`AdminID`),
  UNIQUE KEY `UserID_UNIQUE` (`AdminID`),
  UNIQUE KEY `Email_UNIQUE` (`Email`)
);

-- property
CREATE TABLE `property` (
  `PropertyID` int NOT NULL,
  `PropertyName` varchar(45) DEFAULT NULL,
  `Street` varchar(45) DEFAULT NULL,
  `City` varchar(45) DEFAULT NULL,
  `State` varchar(45) DEFAULT NULL,
  `ZipCode` varchar(45) DEFAULT NULL,
  `Source` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`PropertyID`),
  UNIQUE KEY `PropertyID_UNIQUE` (`PropertyID`)
);

-- listings
CREATE TABLE `listings` (
  `ListingID` int NOT NULL,
  `OwnerID` int NOT NULL,
  `PropertyID` int NOT NULL,
  `SquareFeet` int DEFAULT NULL,
  `Source` varchar(200) DEFAULT NULL,
  `Price` int DEFAULT NULL,
  `Rooms` int DEFAULT NULL,
  `Title` varchar(45) DEFAULT NULL,
  `Bathrooms` int DEFAULT NULL,
  PRIMARY KEY (`ListingID`),
  UNIQUE KEY `ListingID_UNIQUE` (`ListingID`),
  CONSTRAINT `ListingsPropertyID` FOREIGN KEY (`PropertyID`) REFERENCES `property` (`PropertyID`) ON DELETE CASCADE,
  CONSTRAINT `OwnerID` FOREIGN KEY (`OwnerID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
);

-- listing interest
CREATE TABLE `listing_interest` (
  `ListingInterestGroupID` int NOT NULL,
  `ListingID` int NOT NULL,
  `UserID` int NOT NULL,
  PRIMARY KEY (`ListingInterestGroupID`),
  UNIQUE KEY `ListingInterestGroupID_UNIQUE` (`ListingInterestGroupID`),
  CONSTRAINT `ListingID` FOREIGN KEY (`ListingID`) REFERENCES `listings` (`ListingID`) ON DELETE CASCADE,
  CONSTRAINT `ListingInterestUserID` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
);

-- preferences
CREATE TABLE `preferences` (
  `PreferenceID` int NOT NULL,
  `UserID` int NOT NULL,
  `ZipCode` varchar(45) DEFAULT NULL,
  `Budget` int DEFAULT NULL,
  `Rooms` int DEFAULT NULL,
  `PropertyType` varchar(45) DEFAULT NULL,
  `LeaseDuration` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`PreferenceID`),
  UNIQUE KEY `PreferenceID_UNIQUE` (`PreferenceID`),
  UNIQUE KEY `UserID_UNIQUE` (`UserID`),
  CONSTRAINT `PreferencesUserID` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
);

-- reviews
CREATE TABLE `reviews` (
  `ReviewID` int NOT NULL,
  `PropertyID` int NOT NULL,
  `UserID` int NOT NULL,
  `Rating` int DEFAULT NULL,
  `ReviewDate` datetime DEFAULT NULL,
  `Description` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`ReviewID`),
  UNIQUE KEY `ReviewID_UNIQUE` (`ReviewID`),
  CONSTRAINT `PropertyID` FOREIGN KEY (`PropertyID`) REFERENCES `property` (`PropertyID`) ON DELETE CASCADE,
  CONSTRAINT `PropertyUserID` FOREIGN KEY (`UserID`) REFERENCES `users` (`UserID`) ON DELETE CASCADE
);
