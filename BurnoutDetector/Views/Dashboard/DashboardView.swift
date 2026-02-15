import SwiftUI

/// Main dashboard showing burnout score, metric cards, and suggested intervention
struct DashboardView: View {
    @EnvironmentObject var dataStore: DataStore
    @EnvironmentObject var healthService: HealthKitService
    @StateObject private var burnoutEngine = BurnoutEngine()
    @StateObject private var screenTimeService = ScreenTimeService()

    @State private var currentScore: BurnoutScore?
    @State private var suggestedIntervention: Intervention?
    @State private var riskTriggers: [RiskTrigger] = []
    @State private var isLoading = true

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Score Ring
                    scoreSection

                    // Quick Metrics
                    metricsGrid

                    // Risk Triggers
                    if !riskTriggers.isEmpty {
                        riskTriggersSection
                    }

                    // Suggested Intervention
                    if let intervention = suggestedIntervention {
                        suggestedInterventionCard(intervention)
                    }

                    // Mini Trend Chart
                    trendPreview
                }
                .padding()
            }
            .navigationTitle("Dashboard")
            .refreshable {
                await refreshData()
            }
            .task {
                await refreshData()
            }
        }
    }

    // MARK: - Score Section

    private var scoreSection: some View {
        VStack(spacing: 12) {
            if let score = currentScore {
                ScoreRingView(
                    score: score.score,
                    riskLevel: score.riskLevel,
                    size: 200
                )

                Text("Burnout Score")
                    .font(.headline)
                    .foregroundColor(.secondary)
            } else if isLoading {
                ProgressView()
                    .frame(width: 200, height: 200)
            } else {
                ScoreRingView(score: 0, riskLevel: .stable, size: 200)
                Text("Complete a mood check to get your score")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
    }

    // MARK: - Metrics Grid

    private var metricsGrid: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible())
        ], spacing: 12) {
            MetricCardView(
                title: "Sleep",
                value: formatSleepHours(),
                change: formatChange(currentScore?.sleepScore),
                direction: directionFor(currentScore?.sleepScore),
                iconName: "moon.fill"
            )

            MetricCardView(
                title: "Screen Time",
                value: formatScreenTime(),
                change: formatChange(currentScore?.screenTimeScore),
                direction: directionFor(currentScore?.screenTimeScore),
                iconName: "iphone"
            )

            MetricCardView(
                title: "Steps",
                value: formatSteps(),
                change: formatChange(currentScore?.activityScore),
                direction: directionForActivity(currentScore?.activityScore),
                iconName: "figure.walk"
            )

            MetricCardView(
                title: "Mood",
                value: formatMood(),
                change: formatChange(currentScore?.moodScore),
                direction: directionFor(currentScore?.moodScore),
                iconName: "face.smiling"
            )
        }
    }

    // MARK: - Risk Triggers

    private var riskTriggersSection: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Risk Triggers")
                .font(.headline)

            ForEach(riskTriggers) { trigger in
                HStack(spacing: 12) {
                    Circle()
                        .fill(colorForSeverity(trigger.severity))
                        .frame(width: 8, height: 8)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(trigger.metric)
                            .font(.subheadline)
                            .fontWeight(.medium)
                        Text(trigger.message)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()
                }
                .padding(.vertical, 4)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Suggested Intervention

    private func suggestedInterventionCard(_ intervention: Intervention) -> some View {
        NavigationLink(destination: InterventionDetailView(intervention: intervention)) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text("Suggested Reset")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Spacer()
                    Text("\(intervention.durationMinutes) min")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                HStack(spacing: 12) {
                    Image(systemName: intervention.iconName)
                        .font(.title2)
                        .foregroundColor(.blue)

                    VStack(alignment: .leading, spacing: 2) {
                        Text(intervention.title)
                            .font(.headline)
                            .foregroundColor(.primary)
                        Text(intervention.description)
                            .font(.caption)
                            .foregroundColor(.secondary)
                            .lineLimit(2)
                    }

                    Spacer()

                    Image(systemName: "chevron.right")
                        .foregroundColor(.secondary)
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
    }

    // MARK: - Trend Preview

    private var trendPreview: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("7-Day Trend")
                .font(.headline)

            let scores = dataStore.recentScores(days: 7).map { $0.score }
            MiniChartView(
                dataPoints: scores.isEmpty ? [0] : scores,
                color: trendColor(scores),
                height: 80
            )
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Data Refresh

    private func refreshData() async {
        isLoading = true
        let metrics = await healthService.fetchDailyMetrics(for: Date())
        dataStore.saveHealthMetrics(metrics)

        let recentMoods = dataStore.recentMoodEntries(days: 7)
        let score = burnoutEngine.calculateScore(
            metrics: metrics,
            recentMoods: recentMoods,
            screenTimeMinutes: screenTimeService.todayScreenTimeMinutes,
            screenTimeChange: screenTimeService.screenTimeChange
        )

        dataStore.saveBurnoutScore(score)
        currentScore = score
        riskTriggers = burnoutEngine.identifyRiskTriggers(score: score)
        suggestedIntervention = burnoutEngine.suggestIntervention(score: score)
        isLoading = false
    }

    // MARK: - Formatting Helpers

    private func formatSleepHours() -> String {
        if let metrics = dataStore.recentMetrics(days: 1).last,
           let hours = metrics.sleepHours {
            return String(format: "%.1fh", hours)
        }
        return "--"
    }

    private func formatScreenTime() -> String {
        let minutes = screenTimeService.todayScreenTimeMinutes
        if minutes > 0 {
            let hours = minutes / 60
            return String(format: "%.1fh", hours)
        }
        return "--"
    }

    private func formatSteps() -> String {
        if let metrics = dataStore.recentMetrics(days: 1).last,
           let steps = metrics.stepCount {
            if steps >= 1000 {
                return String(format: "%.1fk", Double(steps) / 1000)
            }
            return "\(steps)"
        }
        return "--"
    }

    private func formatMood() -> String {
        if let entry = dataStore.todaysMoodEntry() {
            return entry.mood.emoji
        }
        return "--"
    }

    private func formatChange(_ score: Double?) -> String {
        guard let score = score else { return "--" }
        return "\(Int(score))%"
    }

    private func directionFor(_ score: Double?) -> TrendDirection {
        guard let score = score else { return .stable }
        if score > 60 { return .up }
        if score < 40 { return .down }
        return .stable
    }

    private func directionForActivity(_ score: Double?) -> TrendDirection {
        guard let score = score else { return .stable }
        // For activity, high score means low activity (bad)
        if score > 60 { return .down }
        if score < 40 { return .up }
        return .stable
    }

    private func colorForSeverity(_ severity: RiskTrigger.Severity) -> Color {
        switch severity {
        case .low: return .yellow
        case .medium: return .orange
        case .high: return .red
        }
    }

    private func trendColor(_ scores: [Double]) -> Color {
        guard let last = scores.last else { return .blue }
        switch RiskLevel.from(score: last) {
        case .stable: return .green
        case .atRisk: return .orange
        case .burnoutLikely: return .red
        }
    }
}

#Preview {
    DashboardView()
        .environmentObject(DataStore())
        .environmentObject(HealthKitService())
}
