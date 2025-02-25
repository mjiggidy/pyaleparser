from pyale import Ale, AleEvent

ale = Ale()

event = AleEvent({
	"Name": "Michael",
	"Tape": "A001C003_250520_R1CB",
	"Start": "01:00:00:00",
	"Duration": "01:00:03:20"
})

ale.events.insert(0,event)

print(ale.to_formatted_string())