SELECT PhotoID
FROM Photo
WHERE PhotoID IN 
    (SELECT PhotoID
    FROM (Photo JOIN Person ON (Photo.PhotoPoster=Person.Username)) JOIN Follow ON (Follow.username_followed=Photo.PhotoPoster)
    WHERE followstatus=True AND username_follower="TestUser") OR PhotoID IN 
        (SELECT PhotoID
        FROM SharedWith JOIN BelongTo ON (SharedWith.groupOwner=BelongTo.owner_username AND SharedWith.groupName=BelongTo.groupName)
        WHERE member_username="testuser");