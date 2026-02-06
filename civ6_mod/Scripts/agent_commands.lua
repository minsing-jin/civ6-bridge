-- agent_commands.lua
-- Wrapper functions for Civ6 API, callable via FireTuner.
-- Each function is registered on the Game object so it can be invoked
-- from Python as: GameCore.Game.AgentXxx(...)

--- Wrap a result string with sentinels for Python-side extraction.
local function wrap_result(str)
    return "CIV6BRIDGE_RESULT:" .. str .. ":CIV6BRIDGE_END"
end

--- Move a unit to the given tile coordinates.
function AgentMoveUnit(playerID, unitID, targetX, targetY)
    local pPlayer = Players[playerID]
    if pPlayer == nil then
        print(wrap_result("ERR:invalid player " .. tostring(playerID)))
        return
    end

    local pUnit = pPlayer:GetUnits():FindID(unitID)
    if pUnit == nil then
        print(wrap_result("ERR:unit not found " .. tostring(unitID)))
        return
    end

    UnitManager.RequestOperation(pUnit, UnitOperationTypes.MOVETO, {X = targetX, Y = targetY})
    print(wrap_result("OK:move_unit"))
end

--- End the current player's turn.
function AgentEndTurn()
    local localPlayer = Game.GetLocalPlayer()
    if localPlayer == -1 then
        print(wrap_result("ERR:no local player"))
        return
    end

    local pPlayer = Players[localPlayer]
    if pPlayer == nil then
        print(wrap_result("ERR:invalid local player"))
        return
    end

    local pPlayerUnits = pPlayer:GetUnits()
    if pPlayerUnits then
        for _, pUnit in pPlayerUnits:Members() do
            UnitManager.RequestCommand(pUnit, UnitCommandTypes.CANCEL)
        end
    end

    UI.RequestAction(ActionTypes.ACTION_ENDTURN)
    print(wrap_result("OK:end_turn"))
end

--- Set a player's gold balance to an exact amount.
function AgentSetGold(playerID, amount)
    local pPlayer = Players[playerID]
    if pPlayer == nil then
        print(wrap_result("ERR:invalid player " .. tostring(playerID)))
        return
    end

    local pTreasury = pPlayer:GetTreasury()
    local current = pTreasury:GetGoldBalance()
    local delta = amount - current
    pTreasury:ChangeGoldBalance(delta)
    print(wrap_result("OK:set_gold"))
end

--- Add (or subtract) gold from a player's treasury.
function AgentAddGold(playerID, amount)
    local pPlayer = Players[playerID]
    if pPlayer == nil then
        print(wrap_result("ERR:invalid player " .. tostring(playerID)))
        return
    end

    pPlayer:GetTreasury():ChangeGoldBalance(amount)
    print(wrap_result("OK:add_gold"))
end

--- Set the current research tech for a player.
function AgentResearchTech(playerID, techType)
    local pPlayer = Players[playerID]
    if pPlayer == nil then
        print(wrap_result("ERR:invalid player " .. tostring(playerID)))
        return
    end

    local pTechs = pPlayer:GetTechs()
    local techIndex = nil
    for row in GameInfo.Technologies() do
        if row.Type == techType then
            techIndex = row.Index
            break
        end
    end

    if techIndex == nil then
        print(wrap_result("ERR:unknown tech " .. tostring(techType)))
        return
    end

    pTechs:SetResearchingTech(techIndex)
    print(wrap_result("OK:research_tech"))
end

--- Queue a unit for production in a city.
function AgentProduceUnit(cityID, playerID, unitType)
    local pPlayer = Players[playerID]
    if pPlayer == nil then
        print(wrap_result("ERR:invalid player " .. tostring(playerID)))
        return
    end

    local pCity = pPlayer:GetCities():FindID(cityID)
    if pCity == nil then
        print(wrap_result("ERR:city not found " .. tostring(cityID)))
        return
    end

    local unitIndex = nil
    for row in GameInfo.Units() do
        if row.UnitType == unitType then
            unitIndex = row.Index
            break
        end
    end

    if unitIndex == nil then
        print(wrap_result("ERR:unknown unit type " .. tostring(unitType)))
        return
    end

    pCity:GetBuildQueue():CreateIncompleteUnit(unitIndex)
    print(wrap_result("OK:produce_unit"))
end

--- Simple connectivity check.
function AgentPing()
    print(wrap_result("PONG"))
end

-- Register functions on the Game object for FireTuner access
Game.AgentMoveUnit    = AgentMoveUnit
Game.AgentEndTurn     = AgentEndTurn
Game.AgentSetGold     = AgentSetGold
Game.AgentAddGold     = AgentAddGold
Game.AgentResearchTech = AgentResearchTech
Game.AgentProduceUnit = AgentProduceUnit
Game.AgentPing        = AgentPing

print("[civ6-bridge] Agent commands registered.")
