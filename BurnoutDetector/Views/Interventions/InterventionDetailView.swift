import SwiftUI

/// Detail view for a specific intervention with step-by-step instructions
struct InterventionDetailView: View {
    let intervention: Intervention

    @State private var currentStep = 0
    @State private var isActive = false
    @State private var timeRemaining: Int = 0
    @State private var timer: Timer?
    @State private var breathPhase: BreathPhase = .inhale

    enum BreathPhase: String {
        case inhale = "Breathe In"
        case hold = "Hold"
        case exhale = "Breathe Out"
        case holdOut = "Hold"
    }

    private var categoryColor: Color {
        switch intervention.category {
        case .breathing: return .blue
        case .movement: return .green
        case .social: return .purple
        case .digital: return .orange
        case .sound: return .indigo
        case .emergency: return .red
        }
    }

    var body: some View {
        ScrollView {
            VStack(spacing: 32) {
                // Header
                headerSection

                if isActive && intervention.category == .breathing {
                    breathingGuide
                } else if isActive {
                    activeSession
                } else {
                    instructionsSection
                }

                // Start/Stop Button
                actionButton
            }
            .padding()
        }
        .navigationTitle(intervention.title)
        .navigationBarTitleDisplayMode(.inline)
        .onDisappear {
            stopSession()
        }
    }

    // MARK: - Header

    private var headerSection: some View {
        VStack(spacing: 16) {
            Image(systemName: intervention.iconName)
                .font(.system(size: 48))
                .foregroundColor(categoryColor)
                .frame(width: 96, height: 96)
                .background(categoryColor.opacity(0.15))
                .cornerRadius(24)

            Text(intervention.description)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)

            HStack(spacing: 16) {
                Label("\(intervention.durationMinutes) min", systemImage: "clock")
                Label(intervention.category.rawValue, systemImage: intervention.category.iconName)
            }
            .font(.caption)
            .foregroundColor(.secondary)
        }
    }

    // MARK: - Instructions

    private var instructionsSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Instructions")
                .font(.headline)

            ForEach(Array(intervention.instructions.enumerated()), id: \.offset) { index, step in
                HStack(alignment: .top, spacing: 12) {
                    Text("\(index + 1)")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .frame(width: 24, height: 24)
                        .background(categoryColor)
                        .cornerRadius(12)

                    Text(step)
                        .font(.body)
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Breathing Guide

    private var breathingGuide: some View {
        VStack(spacing: 24) {
            // Animated breathing circle
            Circle()
                .fill(categoryColor.opacity(0.3))
                .frame(
                    width: breathPhase == .inhale || breathPhase == .hold ? 200 : 120,
                    height: breathPhase == .inhale || breathPhase == .hold ? 200 : 120
                )
                .overlay(
                    Text(breathPhase.rawValue)
                        .font(.title3)
                        .fontWeight(.medium)
                        .foregroundColor(categoryColor)
                )
                .animation(.easeInOut(duration: 4), value: breathPhase)

            // Timer
            Text(formatTime(timeRemaining))
                .font(.system(size: 48, weight: .light, design: .rounded))
                .monospacedDigit()

            // Current step
            if currentStep < intervention.instructions.count {
                Text(intervention.instructions[currentStep])
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
        }
    }

    // MARK: - Active Session

    private var activeSession: some View {
        VStack(spacing: 24) {
            // Timer
            Text(formatTime(timeRemaining))
                .font(.system(size: 64, weight: .light, design: .rounded))
                .monospacedDigit()

            // Progress
            ProgressView(value: sessionProgress)
                .tint(categoryColor)

            // Current step
            if currentStep < intervention.instructions.count {
                VStack(spacing: 8) {
                    Text("Step \(currentStep + 1) of \(intervention.instructions.count)")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Text(intervention.instructions[currentStep])
                        .font(.title3)
                        .fontWeight(.medium)
                        .multilineTextAlignment(.center)
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)

                // Navigation
                HStack(spacing: 20) {
                    Button("Previous") {
                        if currentStep > 0 { currentStep -= 1 }
                    }
                    .disabled(currentStep == 0)

                    Button("Next") {
                        if currentStep < intervention.instructions.count - 1 {
                            currentStep += 1
                        }
                    }
                    .disabled(currentStep >= intervention.instructions.count - 1)
                }
                .font(.subheadline)
            }
        }
    }

    // MARK: - Action Button

    private var actionButton: some View {
        Button(action: {
            if isActive {
                stopSession()
            } else {
                startSession()
            }
        }) {
            Text(isActive ? "Stop" : "Start")
                .font(.headline)
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding()
                .background(isActive ? Color.red : categoryColor)
                .cornerRadius(12)
        }
    }

    // MARK: - Session Control

    private func startSession() {
        isActive = true
        currentStep = 0
        timeRemaining = intervention.durationMinutes * 60

        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            if timeRemaining > 0 {
                timeRemaining -= 1

                // Update breath phase every 4 seconds for breathing exercises
                if intervention.category == .breathing {
                    let phase = (intervention.durationMinutes * 60 - timeRemaining) % 16
                    switch phase {
                    case 0..<4: breathPhase = .inhale
                    case 4..<8: breathPhase = .hold
                    case 8..<12: breathPhase = .exhale
                    case 12..<16: breathPhase = .holdOut
                    default: break
                    }
                }
            } else {
                stopSession()
            }
        }
    }

    private func stopSession() {
        isActive = false
        timer?.invalidate()
        timer = nil
    }

    private var sessionProgress: Double {
        let total = Double(intervention.durationMinutes * 60)
        guard total > 0 else { return 0 }
        return 1.0 - (Double(timeRemaining) / total)
    }

    private func formatTime(_ seconds: Int) -> String {
        let mins = seconds / 60
        let secs = seconds % 60
        return String(format: "%d:%02d", mins, secs)
    }
}

#Preview {
    NavigationStack {
        InterventionDetailView(intervention: InterventionLibrary.all[0])
    }
}
