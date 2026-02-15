import Foundation

/// A micro-intervention suggested when burnout risk rises
struct Intervention: Codable, Identifiable {
    let id: UUID
    let title: String
    let description: String
    let category: InterventionCategory
    let durationMinutes: Int
    let iconName: String
    let instructions: [String]

    init(
        id: UUID = UUID(),
        title: String,
        description: String,
        category: InterventionCategory,
        durationMinutes: Int,
        iconName: String,
        instructions: [String]
    ) {
        self.id = id
        self.title = title
        self.description = description
        self.category = category
        self.durationMinutes = durationMinutes
        self.iconName = iconName
        self.instructions = instructions
    }
}

enum InterventionCategory: String, Codable, CaseIterable {
    case breathing = "Breathing"
    case movement = "Movement"
    case social = "Social"
    case digital = "Digital Detox"
    case sound = "Sound Therapy"
    case emergency = "Emergency Reset"

    var iconName: String {
        switch self {
        case .breathing: return "wind"
        case .movement: return "figure.walk"
        case .social: return "message.fill"
        case .digital: return "iphone.slash"
        case .sound: return "waveform"
        case .emergency: return "heart.circle.fill"
        }
    }

    var color: String {
        switch self {
        case .breathing: return "blue"
        case .movement: return "green"
        case .social: return "purple"
        case .digital: return "orange"
        case .sound: return "indigo"
        case .emergency: return "red"
        }
    }
}

/// Pre-built interventions library
struct InterventionLibrary {
    static let all: [Intervention] = [
        Intervention(
            title: "Box Breathing",
            description: "Calm your nervous system with a 2-minute breathing exercise",
            category: .breathing,
            durationMinutes: 2,
            iconName: "wind",
            instructions: [
                "Find a comfortable position",
                "Breathe in for 4 seconds",
                "Hold for 4 seconds",
                "Breathe out for 4 seconds",
                "Hold for 4 seconds",
                "Repeat 6 times"
            ]
        ),
        Intervention(
            title: "4-7-8 Breathing",
            description: "Deep relaxation technique to reduce stress",
            category: .breathing,
            durationMinutes: 3,
            iconName: "wind",
            instructions: [
                "Sit with your back straight",
                "Breathe in through your nose for 4 seconds",
                "Hold your breath for 7 seconds",
                "Exhale completely through your mouth for 8 seconds",
                "Repeat 4 times"
            ]
        ),
        Intervention(
            title: "10-Minute Walk",
            description: "Step outside and move your body to reset your mind",
            category: .movement,
            durationMinutes: 10,
            iconName: "figure.walk",
            instructions: [
                "Put your phone on silent",
                "Step outside",
                "Walk at a comfortable pace",
                "Focus on your surroundings",
                "Notice 5 things you can see",
                "Return when you feel calmer"
            ]
        ),
        Intervention(
            title: "Quick Stretch",
            description: "Release tension with a 3-minute desk stretch routine",
            category: .movement,
            durationMinutes: 3,
            iconName: "figure.flexibility",
            instructions: [
                "Stand up from your desk",
                "Roll your shoulders 10 times",
                "Stretch your neck side to side",
                "Reach arms overhead and stretch",
                "Touch your toes (or try)",
                "Shake out your hands and arms"
            ]
        ),
        Intervention(
            title: "Text Someone",
            description: "Reach out to a friend or loved one — connection helps",
            category: .social,
            durationMinutes: 2,
            iconName: "message.fill",
            instructions: [
                "Think of someone who makes you smile",
                "Send them a simple message",
                "It can be as simple as 'Hey, thinking of you'",
                "Don't overthink it — just connect"
            ]
        ),
        Intervention(
            title: "Screen Break",
            description: "Block 30 minutes of no-screen time to let your eyes and mind rest",
            category: .digital,
            durationMinutes: 30,
            iconName: "iphone.slash",
            instructions: [
                "Set a 30-minute timer",
                "Put your phone face down",
                "Step away from your computer",
                "Do something with your hands",
                "Read a physical book, draw, or just sit",
                "Return to screens only after the timer"
            ]
        ),
        Intervention(
            title: "Nervous System Reset",
            description: "5-minute audio session to calm your fight-or-flight response",
            category: .sound,
            durationMinutes: 5,
            iconName: "waveform",
            instructions: [
                "Put on headphones",
                "Close your eyes",
                "Listen to the calming frequency",
                "Breathe naturally",
                "Let the sound wash over you"
            ]
        ),
        Intervention(
            title: "Overwhelmed Mode",
            description: "Emergency reset when everything feels like too much",
            category: .emergency,
            durationMinutes: 5,
            iconName: "heart.circle.fill",
            instructions: [
                "Stop everything right now",
                "Put your hand on your chest",
                "Take 5 slow, deep breaths",
                "Name 5 things you can see",
                "Name 4 things you can touch",
                "Name 3 things you can hear",
                "Name 2 things you can smell",
                "Name 1 thing you can taste",
                "You are safe. You are okay."
            ]
        )
    ]
}
