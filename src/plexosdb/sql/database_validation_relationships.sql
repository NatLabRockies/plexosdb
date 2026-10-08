SELECT
    'objects' AS category,
    't_object.object_id=' || obj.object_id || ' is missing required class_id.' AS message,
    NULL AS object_id,
    NULL AS attribute_id,
    NULL AS value
FROM t_object AS obj
WHERE obj.class_id IS NULL

UNION ALL

SELECT
    'objects',
    't_object.object_id=' || obj.object_id || ' has class_id=' || obj.class_id ||
        ', but category_id=' || category.category_id || ' belongs to class_id=' || category.class_id || '.',
    NULL,
    NULL,
    NULL
FROM t_object AS obj
JOIN t_category AS category ON category.category_id = obj.category_id
WHERE obj.class_id IS NOT NULL
  AND obj.class_id != category.class_id

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership_id || ' is missing required parent_class_id.',
    NULL,
    NULL,
    NULL
FROM t_membership
WHERE parent_class_id IS NULL

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership_id || ' is missing required parent_object_id.',
    NULL,
    NULL,
    NULL
FROM t_membership
WHERE parent_object_id IS NULL

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership_id || ' is missing required collection_id.',
    NULL,
    NULL,
    NULL
FROM t_membership
WHERE collection_id IS NULL

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership_id || ' is missing required child_class_id.',
    NULL,
    NULL,
    NULL
FROM t_membership
WHERE child_class_id IS NULL

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership_id || ' is missing required child_object_id.',
    NULL,
    NULL,
    NULL
FROM t_membership
WHERE child_object_id IS NULL

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership.membership_id || ' has parent_class_id=' ||
        membership.parent_class_id || ', but the parent object class_id is ' ||
        COALESCE(CAST(parent.class_id AS TEXT), 'NULL') || '.',
    NULL,
    NULL,
    NULL
FROM t_membership AS membership
JOIN t_object AS parent ON parent.object_id = membership.parent_object_id
WHERE membership.parent_class_id IS NOT NULL
  AND membership.parent_class_id IS NOT parent.class_id

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership.membership_id || ' has child_class_id=' ||
        membership.child_class_id || ', but the child object class_id is ' ||
        COALESCE(CAST(child.class_id AS TEXT), 'NULL') || '.',
    NULL,
    NULL,
    NULL
FROM t_membership AS membership
JOIN t_object AS child ON child.object_id = membership.child_object_id
WHERE membership.child_class_id IS NOT NULL
  AND membership.child_class_id IS NOT child.class_id

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership.membership_id || ' has parent_class_id=' ||
        membership.parent_class_id || ', but the collection parent class_id is ' ||
        COALESCE(CAST(collection.parent_class_id AS TEXT), 'NULL') || '.',
    NULL,
    NULL,
    NULL
FROM t_membership AS membership
JOIN t_collection AS collection ON collection.collection_id = membership.collection_id
WHERE membership.parent_class_id IS NOT NULL
  AND membership.parent_class_id IS NOT collection.parent_class_id

UNION ALL

SELECT
    'memberships',
    't_membership.membership_id=' || membership.membership_id || ' has child_class_id=' ||
        membership.child_class_id || ', but the collection child class_id is ' ||
        COALESCE(CAST(collection.child_class_id AS TEXT), 'NULL') || '.',
    NULL,
    NULL,
    NULL
FROM t_membership AS membership
JOIN t_collection AS collection ON collection.collection_id = membership.collection_id
WHERE membership.child_class_id IS NOT NULL
  AND membership.child_class_id IS NOT collection.child_class_id

UNION ALL

SELECT
    'attributes',
    't_attribute_data for object_id=' || data.object_id || ' and attribute_id=' || data.attribute_id ||
        ' connects class_id=' || COALESCE(CAST(obj.class_id AS TEXT), 'NULL') ||
        ' to an attribute for class_id=' || COALESCE(CAST(attribute.class_id AS TEXT), 'NULL') || '.',
    NULL,
    NULL,
    NULL
FROM t_attribute_data AS data
JOIN t_object AS obj ON obj.object_id = data.object_id
JOIN t_attribute AS attribute ON attribute.attribute_id = data.attribute_id
WHERE attribute.class_id IS NULL
   OR obj.class_id IS NOT attribute.class_id

UNION ALL

SELECT
    'properties',
    't_data.data_id=' || data_id || ' is missing required membership_id.',
    NULL,
    NULL,
    NULL
FROM t_data
WHERE membership_id IS NULL

UNION ALL

SELECT
    'properties',
    't_data.data_id=' || data_id || ' is missing required property_id.',
    NULL,
    NULL,
    NULL
FROM t_data
WHERE property_id IS NULL

UNION ALL

SELECT
    'properties',
    't_data.data_id=' || data.data_id || ' uses property_id=' || data.property_id || ' from collection_id=' ||
        COALESCE(CAST(property.collection_id AS TEXT), 'NULL') || ', but membership_id=' ||
        data.membership_id || ' uses collection_id=' || COALESCE(CAST(membership.collection_id AS TEXT), 'NULL') || '.',
    NULL,
    NULL,
    NULL
FROM t_data AS data
JOIN t_property AS property ON property.property_id = data.property_id
JOIN t_membership AS membership ON membership.membership_id = data.membership_id
WHERE property.collection_id IS NOT membership.collection_id

UNION ALL

SELECT
    'types',
    NULL,
    data.object_id,
    data.attribute_id,
    data.value
FROM t_attribute_data AS data
JOIN t_attribute AS attribute ON attribute.attribute_id = data.attribute_id
WHERE attribute.is_integer = 1
  AND data.value IS NOT NULL;
