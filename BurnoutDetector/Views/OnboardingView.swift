import SwiftUI

/// Onboarding flow: explains the app and requests permissions
struct OnboardingView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var healthService: HealthKitService

    @State private var currentPage = 0

    private let pages: [OnboardingPage] = [
        OnboardingPage(
            iconName: "gauge.medium",
            title: "Detect Burnout Early",
            description: "We analyze your sleep, activity, screen time, and mood to detect burnout before you feel it.",
            color: .blue
        ),
        OnboardingPage(
            iconName: "face.smiling",
            title: "10-Second Daily Check-In",
            description: "One quick mood check per day helps our prediction get smarter over time.",
            color: .yellow
        ),
        OnboardingPage(
            iconName: "chart.line.uptrend.xyaxis",
            title: "See Your Patterns",
            description: "Track trends over time and understand what triggers your stress.",
            color: .green
        ),
        OnboardingPage(
            iconName: "heart.circle.fill",
            title: "Micro Interventions",
            description: "When risk rises, get quick 2–5 minute resets to calm your nervous system.",
            color: .red
        )
    ]

    var body: some View {
        VStack(spacing: 0) {
            // Page content
            TabView(selection: $currentPage) {
                ForEach(Array(pages.enumerated()), id: \.offset) { index, page in
                    pageView(page)
                        .tag(index)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))

            // Bottom section
            VStack(spacing: 16) {
                if currentPage == pages.count - 1 {
                    // Final page: permission + start
                    Button(action: completeOnboarding) {
                        Text("Get Started")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(12)
                    }

                    Text("Your data stays on your device. Always.")
                        .font(.caption)
                        .foregroundColor(.secondary)
                } else {
                    Button(action: { withAnimation { currentPage += 1 } }) {
                        Text("Next")
                            .font(.headline)
                            .foregroundColor(.white)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .cornerRadius(12)
                    }

                    Button("Skip") {
                        completeOnboarding()
                    }
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                }
            }
            .padding(.horizontal, 24)
            .padding(.bottom, 32)
        }
    }

    private func pageView(_ page: OnboardingPage) -> some View {
        VStack(spacing: 24) {
            Spacer()

            Image(systemName: page.iconName)
                .font(.system(size: 72))
                .foregroundColor(page.color)

            Text(page.title)
                .font(.title)
                .fontWeight(.bold)
                .multilineTextAlignment(.center)

            Text(page.description)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal, 32)

            Spacer()
        }
    }

    private func completeOnboarding() {
        Task {
            _ = await healthService.requestAuthorization()
        }
        withAnimation {
            appState.hasCompletedOnboarding = true
        }
    }
}

struct OnboardingPage {
    let iconName: String
    let title: String
    let description: String
    let color: Color
}

#Preview {
    OnboardingView()
        .environmentObject(AppState())
        .environmentObject(HealthKitService())
}
