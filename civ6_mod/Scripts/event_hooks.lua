-- event_hooks.lua
-- Subscribes ExportGameState to Civ6 game events.

include("game_state")
include("agent_commands")

--- Called when a player's turn starts.
local function OnPlayerTurnStarted(player_id)
    -- Only export on the human player's turn to avoid spamming the log.
    if Players[player_id]:IsHuman() then
        ExportGameState()
    end
end

--- Called when the loading screen closes (game is ready).
local function OnLoadScreenClose()
    ExportGameState()
end

-- Register event handlers
Events.PlayerTurnStarted.Add(OnPlayerTurnStarted)
Events.LoadScreenClose.Add(OnLoadScreenClose)

print("[civ6-bridge] Event hooks registered.")
