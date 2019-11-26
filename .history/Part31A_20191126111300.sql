SELECT DISTINCT photoID, photoPoster 
FROM Photo 
WHERE photoPoster = "TestUser"
OR (photoID, photoPoster) IN
    (SELECT photoID, photoPoster 
    FROM (Photo AS P JOIN Follow AS F ON (F.username_followed=P.photoPoster)) 
    WHERE followstatus=TRUE AND P.allFollowers=True AND F.username_follower = "TestUser") 
OR (photoID, photoPoster) IN 
    (SELECT photoID, photoPoster 
    FROM SharedWith JOIN BelongTo ON (SharedWith.groupOwner= BelongTo.owner_username AND SharedWith.groupName=BelongTo.groupName))
    WHERE SharedWith.photoID = photoID AND BelongTo.member_username = "TestUser")
