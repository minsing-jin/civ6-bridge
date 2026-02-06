-- game_state.lua
-- Serializes the current Civ6 game state to JSON and prints it
-- with sentinel delimiters so the Python side can parse Lua.log.

include("json")
include("utils")

local SENTINEL_BEGIN = "[CIV6BRIDGE_BEGIN_v1]"
local SENTINEL_END   = "[CIV6BRIDGE_END_v1]"

--- Build a city data table from a pCity object.
local function export_city(pCity, owner_id)
    local city_data = {
        id         = pCity:GetID(),
        name       = pCity:GetName(),
        x          = pCity:GetX(),
        y          = pCity:GetY(),
        population = pCity:GetPopulation(),
        owner_id   = owner_id,
        buildings  = {},
        districts  = {},
    }

    -- Collect buildings
    local pBuildings = pCity:GetBuildings()
    if pBuildings then
        for row in GameInfo.Buildings() do
            if pBuildings:HasBuilding(row.Index) then
                city_data.buildings[#city_data.buildings + 1] = row.BuildingType
            end
        end
    end

    -- Collect districts
    local pDistricts = pCity:GetDistricts()
    if pDistricts then
        for _, pDistrict in pDistricts:Members() do
            local district_type = utils.get_type_name(GameInfo.Districts, pDistrict:GetType())
            city_data.districts[#city_data.districts + 1] = district_type
        end
    end

    return city_data
end

--- Build a unit data table from a pUnit object.
local function export_unit(pUnit, owner_id)
    local unit_type_id = pUnit:GetType()
    local unit_info = GameInfo.Units[unit_type_id]
    local unit_type = "UNKNOWN"
    local unit_name = "Unknown"
    local base_combat = 0
    local ranged_combat = 0
    local unit_range = 0
    local base_moves = 2

    if unit_info then
        unit_type    = unit_info.UnitType or "UNKNOWN"
        unit_name    = unit_info.Name or "Unknown"
        base_combat  = unit_info.Combat or 0
        ranged_combat = unit_info.RangedCombat or 0
        unit_range   = unit_info.Range or 0
        base_moves   = unit_info.BaseMoves or 2
    end

    return {
        id              = pUnit:GetID(),
        type            = unit_type,
        name            = unit_name,
        x               = pUnit:GetX(),
        y               = pUnit:GetY(),
        owner_id        = owner_id,
        moves_remaining = pUnit:GetMovesRemaining(),
        max_moves       = pUnit:GetMaxMoves(),
        combat          = base_combat,
        ranged_combat   = ranged_combat,
        range           = unit_range,
        base_moves      = base_moves,
    }
end

--- Build a player data table from a player ID.
local function export_player(player_id)
    local pPlayer = Players[player_id]
    if pPlayer == nil then
        return nil
    end

    local player_data = {
        id        = player_id,
        is_alive  = pPlayer:IsAlive(),
        is_human  = pPlayer:IsHuman(),
    }

    -- Civilization & leader info
    local pConfig = PlayerConfigurations[player_id]
    if pConfig then
        player_data.civilization = pConfig:GetCivilizationTypeName() or "UNKNOWN"
        player_data.leader       = pConfig:GetLeaderTypeName() or "UNKNOWN"
    else
        player_data.civilization = "UNKNOWN"
        player_data.leader       = "UNKNOWN"
    end

    -- Treasury
    local pTreasury = utils.safe_get(pPlayer, "GetTreasury")
    if pTreasury then
        player_data.treasury = {
            gold_balance      = utils.safe_get(pTreasury, "GetGoldBalance") or 0,
            gold_yield        = utils.safe_get(pTreasury, "GetGoldYield") or 0,
            total_maintenance = utils.safe_get(pTreasury, "GetTotalMaintenance") or 0,
        }
    else
        player_data.treasury = { gold_balance = 0, gold_yield = 0, total_maintenance = 0 }
    end

    -- Culture
    local pCulture = utils.safe_get(pPlayer, "GetCulture")
    if pCulture then
        local civic_id = utils.safe_get(pCulture, "GetProgressingCivic")
        local civic_name = ""
        if civic_id and civic_id >= 0 then
            civic_name = utils.get_type_name(GameInfo.Civics, civic_id)
        end
        player_data.culture = { progressing_civic = civic_name }
    else
        player_data.culture = { progressing_civic = "" }
    end

    -- Religion
    local pReligion = utils.safe_get(pPlayer, "GetReligion")
    if pReligion then
        player_data.religion = {
            faith_balance = utils.safe_get(pReligion, "GetFaithBalance") or 0,
            faith_yield   = utils.safe_get(pReligion, "GetFaithYield") or 0,
        }
    else
        player_data.religion = { faith_balance = 0, faith_yield = 0 }
    end

    -- Science
    local pTechs = utils.safe_get(pPlayer, "GetTechs")
    if pTechs then
        local tech_id = utils.safe_get(pTechs, "GetResearchingTech")
        local tech_name = ""
        if tech_id and tech_id >= 0 then
            tech_name = utils.get_type_name(GameInfo.Technologies, tech_id)
        end
        player_data.science = {
            progressing_tech = tech_name,
            science_yield    = utils.safe_get(pTechs, "GetScienceYield") or 0,
        }
    else
        player_data.science = { progressing_tech = "", science_yield = 0 }
    end

    -- Cities
    player_data.cities = {}
    local pCities = utils.safe_get(pPlayer, "GetCities")
    if pCities then
        for _, pCity in pCities:Members() do
            player_data.cities[#player_data.cities + 1] = export_city(pCity, player_id)
        end
    end

    -- Units
    player_data.units = {}
    local pUnits = utils.safe_get(pPlayer, "GetUnits")
    if pUnits then
        for _, pUnit in pUnits:Members() do
            player_data.units[#player_data.units + 1] = export_unit(pUnit, player_id)
        end
    end

    return player_data
end

--- Export the full game state as sentinel-delimited JSON via print().
function ExportGameState()
    local state = {
        version = 1,
        turn    = Game.GetCurrentGameTurn(),
        players = {},
    }

    local player_count = PlayerManager.GetWasEverAliveCount()
    for i = 0, player_count - 1 do
        local player_data = export_player(i)
        if player_data then
            state.players[#state.players + 1] = player_data
        end
    end

    local json_str = json.encode(state)
    print(SENTINEL_BEGIN)
    print(json_str)
    print(SENTINEL_END)
end
