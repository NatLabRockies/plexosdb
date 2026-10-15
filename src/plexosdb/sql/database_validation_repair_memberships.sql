UPDATE t_membership
SET parent_class_id = (
    SELECT endpoint.class_id
    FROM t_object AS endpoint
    JOIN t_collection AS collection
        ON collection.collection_id = t_membership.collection_id
    WHERE endpoint.object_id = t_membership.parent_object_id
      AND endpoint.class_id IS NOT NULL
      AND endpoint.class_id = collection.parent_class_id
)
WHERE t_membership.parent_class_id IS NOT (
    SELECT endpoint.class_id
    FROM t_object AS endpoint
    JOIN t_collection AS collection
        ON collection.collection_id = t_membership.collection_id
    WHERE endpoint.object_id = t_membership.parent_object_id
      AND endpoint.class_id IS NOT NULL
      AND endpoint.class_id = collection.parent_class_id
)
AND EXISTS (
    SELECT 1
    FROM t_object AS endpoint
    JOIN t_collection AS collection
        ON collection.collection_id = t_membership.collection_id
    WHERE endpoint.object_id = t_membership.parent_object_id
      AND endpoint.class_id IS NOT NULL
      AND endpoint.class_id = collection.parent_class_id
);

UPDATE t_membership
SET child_class_id = (
    SELECT endpoint.class_id
    FROM t_object AS endpoint
    JOIN t_collection AS collection
        ON collection.collection_id = t_membership.collection_id
    WHERE endpoint.object_id = t_membership.child_object_id
      AND endpoint.class_id IS NOT NULL
      AND endpoint.class_id = collection.child_class_id
)
WHERE t_membership.child_class_id IS NOT (
    SELECT endpoint.class_id
    FROM t_object AS endpoint
    JOIN t_collection AS collection
        ON collection.collection_id = t_membership.collection_id
    WHERE endpoint.object_id = t_membership.child_object_id
      AND endpoint.class_id IS NOT NULL
      AND endpoint.class_id = collection.child_class_id
)
AND EXISTS (
    SELECT 1
    FROM t_object AS endpoint
    JOIN t_collection AS collection
        ON collection.collection_id = t_membership.collection_id
    WHERE endpoint.object_id = t_membership.child_object_id
      AND endpoint.class_id IS NOT NULL
      AND endpoint.class_id = collection.child_class_id
);
