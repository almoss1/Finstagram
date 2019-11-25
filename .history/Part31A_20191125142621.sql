SELECT PhotoID
FROM Photo
WHERE PhotoID IN 
    (SELECT PhotoID
    FROM (Photo JOIN Person ON (Photo.PhotoPoster=Person.Username)) JOIN Follow ON (Follow.username_followed=Photo.PhotoPoster)
    WHERE followstatus=True AND username_follower="TestUser") OR PhotoID IN 
        (SELECT PhotoID
        FROM SharedWith JOIN BelongTo ON (SharedWith.groupOwner=BelongTo.owner_username AND SharedWith.groupName=BelongTo.groupName)
        WHERE member_username="testuser");


SELECT DISTINCT photoID, photoPoster 
FROM Photo 
WHERE (photoID, photoPoster) IN
    (SELECT photoID, photoPoster 
    FROM (Photo AS P JOIN Follow AS F ON (F.username_followed=P.photoPoster)) 
    WHERE followstatus=TRUE and P.allFollowers=True) 
OR photoPoster = "TestUser"
OR (photoID, photoPoster) IN 
    (SELECT photoID, photoPoster FROM SharedWith JOIN BelongTo ON (SharedWith.groupOwner= BelongTo.owner_username AND SharedWith.groupName=BelongTo.groupName))
