-- json.lua
-- Pure-Lua JSON encoder for Civ6 (no external dependencies).
-- Only encoding is needed; decoding happens on the Python side.

local json = {}

local escape_map = {
    ["\\"] = "\\\\",
    ['"']  = '\\"',
    ["\n"] = "\\n",
    ["\r"] = "\\r",
    ["\t"] = "\\t",
    ["\b"] = "\\b",
    ["\f"] = "\\f",
}

local function escape_string(s)
    return s:gsub('[\\"\n\r\t\b\f]', escape_map)
end

local function is_array(t)
    local count = 0
    for _ in pairs(t) do
        count = count + 1
    end
    if count == 0 then
        return true
    end
    return t[1] ~= nil and count == #t
end

local encode_value  -- forward declaration

local function encode_string(val)
    return '"' .. escape_string(tostring(val)) .. '"'
end

local function encode_number(val)
    if val ~= val then
        return '"NaN"'
    elseif val == math.huge then
        return '"Infinity"'
    elseif val == -math.huge then
        return '"-Infinity"'
    elseif val == math.floor(val) and math.abs(val) < 2^53 then
        return string.format("%d", val)
    else
        return string.format("%.6f", val)
    end
end

local function encode_array(t)
    local parts = {}
    for i = 1, #t do
        parts[i] = encode_value(t[i])
    end
    return "[" .. table.concat(parts, ",") .. "]"
end

local function encode_object(t)
    local parts = {}
    -- Sort keys for deterministic output
    local keys = {}
    for k, _ in pairs(t) do
        if type(k) == "string" then
            keys[#keys + 1] = k
        end
    end
    table.sort(keys)
    for _, k in ipairs(keys) do
        parts[#parts + 1] = encode_string(k) .. ":" .. encode_value(t[k])
    end
    return "{" .. table.concat(parts, ",") .. "}"
end

function encode_value(val)
    local vtype = type(val)
    if val == nil then
        return "null"
    elseif vtype == "boolean" then
        return val and "true" or "false"
    elseif vtype == "number" then
        return encode_number(val)
    elseif vtype == "string" then
        return encode_string(val)
    elseif vtype == "table" then
        if is_array(val) then
            return encode_array(val)
        else
            return encode_object(val)
        end
    else
        return "null"
    end
end

function json.encode(val)
    return encode_value(val)
end

return json
