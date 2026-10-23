SELECT object.object_id, object.name
FROM t_object AS object
WHERE object.object_id != 1
  AND NOT EXISTS (
      SELECT 1
      FROM t_membership AS membership
      WHERE membership.parent_class_id = ?
        AND membership.child_object_id = object.object_id
  )
