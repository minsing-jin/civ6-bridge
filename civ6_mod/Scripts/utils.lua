-- utils.lua
-- Safe accessor helpers for Civ6 Lua API objects.

local utils = {}

--- Safely call a method on an object, returning nil on failure.
-- @param obj  The object to call the method on.
-- @param method  The method name (string).
-- @return The result of obj:method(), or nil if the call fails.
function utils.safe_get(obj, method)
    if obj == nil then
        return nil
    end
    local ok, result = pcall(function()
        return obj[method](obj)
    end)
    if ok then
        return result
    end
    return nil
end

--- Look up a type name from a GameInfo table by type ID.
-- @param info_table  A GameInfo table (e.g. GameInfo.Units).
-- @param type_id  The integer type ID.
-- @return The Type string (e.g. "UNIT_WARRIOR"), or "UNKNOWN".
function utils.get_type_name(info_table, type_id)
    if info_table == nil or type_id == nil then
        return "UNKNOWN"
    end
    for row in info_table() do
        if row.Index == type_id then
            return row.Type or "UNKNOWN"
        end
    end
    return "UNKNOWN"
end

return utils
