import SwiftUI

/// 7-day trends screen with charts and risk trigger breakdown
struct TrendsView: View {
    @EnvironmentObject var dataStore: DataStore

    @State private var selectedTimeRange: TimeRange = .week

    enum TimeRange: String, CaseIterable {
        case week = "7 Days"
        case twoWeeks = "14 Days"
        case month = "30 Days"

        var days: Int {
            switch self {
            case .week: return 7
            case .twoWeeks: return 14
            case .month: return 30
            }
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 24) {
                    // Time Range Picker
                    Picker("Time Range", selection: $selectedTimeRange) {
                        ForEach(TimeRange.allCases, id: \.self) { range in
                            Text(range.rawValue).tag(range)
                        }
                    }
                    .pickerStyle(.segmented)

                    // Burnout Score Trend
                    burnoutScoreTrend

                    // Sleep Consistency Chart
                    sleepTrend

                    // Mood Heatmap
                    moodHeatmap

                    // Activity Trend
                    activityTrend

                    // Risk Triggers Breakdown
                    riskBreakdown
                }
                .padding()
            }
            .navigationTitle("Trends")
        }
    }

    // MARK: - Burnout Score Trend

    private var burnoutScoreTrend: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Burnout Score")
                    .font(.headline)
                Spacer()
                if let latest = dataStore.recentScores(days: selectedTimeRange.days).last {
                    Text("\(Int(latest.score))")
                        .font(.title3)
                        .fontWeight(.bold)
                        .foregroundColor(colorForRisk(latest.riskLevel))
                }
            }

            let scores = dataStore.recentScores(days: selectedTimeRange.days).map { $0.score }
            MiniChartView(
                dataPoints: scores.isEmpty ? [0] : scores,
                color: .orange,
                height: 120
            )

            // Score range labels
            HStack {
                Text("0 Stable")
                    .font(.caption2)
                    .foregroundColor(.green)
                Spacer()
                Text("40 At Risk")
                    .font(.caption2)
                    .foregroundColor(.yellow)
                Spacer()
                Text("70+ Burnout")
                    .font(.caption2)
                    .foregroundColor(.red)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Sleep Trend

    private var sleepTrend: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "moon.fill")
                    .foregroundColor(.indigo)
                Text("Sleep")
                    .font(.headline)
                Spacer()
                if let latest = dataStore.recentMetrics(days: 1).last,
                   let hours = latest.sleepHours {
                    Text(String(format: "%.1fh", hours))
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }

            let sleepData = dataStore.recentMetrics(days: selectedTimeRange.days)
                .compactMap { $0.sleepHours }
            MiniChartView(
                dataPoints: sleepData.isEmpty ? [0] : sleepData,
                color: .indigo,
                height: 80
            )

            // Target line indicator
            HStack {
                Rectangle()
                    .fill(Color.green.opacity(0.5))
                    .frame(height: 1)
                Text("7.5h target")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Mood Heatmap

    private var moodHeatmap: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "face.smiling")
                    .foregroundColor(.yellow)
                Text("Mood")
                    .font(.headline)
            }

            let entries = dataStore.recentMoodEntries(days: selectedTimeRange.days)

            if entries.isEmpty {
                Text("Start checking in daily to see your mood pattern")
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .padding(.vertical, 20)
            } else {
                // Mood grid
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 4), count: 7), spacing: 4) {
                    ForEach(entries) { entry in
                        VStack(spacing: 2) {
                            RoundedRectangle(cornerRadius: 4)
                                .fill(moodColor(entry.mood))
                                .frame(height: 30)
                                .overlay(
                                    Text(entry.mood.emoji)
                                        .font(.caption)
                                )
                            Text(shortDate(entry.date))
                                .font(.system(size: 8))
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // Legend
                HStack(spacing: 12) {
                    ForEach(MoodLevel.allCases.reversed(), id: \.rawValue) { mood in
                        HStack(spacing: 4) {
                            Circle()
                                .fill(moodColor(mood))
                                .frame(width: 8, height: 8)
                            Text(mood.label)
                                .font(.caption2)
                        }
                    }
                }
                .padding(.top, 4)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Activity Trend

    private var activityTrend: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "figure.walk")
                    .foregroundColor(.green)
                Text("Activity")
                    .font(.headline)
                Spacer()
                if let latest = dataStore.recentMetrics(days: 1).last,
                   let steps = latest.stepCount {
                    Text("\(steps) steps")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
            }

            let stepData = dataStore.recentMetrics(days: selectedTimeRange.days)
                .compactMap { $0.stepCount }
                .map { Double($0) }
            MiniChartView(
                dataPoints: stepData.isEmpty ? [0] : stepData,
                color: .green,
                height: 80
            )
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Risk Breakdown

    private var riskBreakdown: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Score Breakdown")
                .font(.headline)

            if let latest = dataStore.latestScore {
                VStack(spacing: 8) {
                    ScoreBarView(label: "Sleep", score: latest.sleepScore, color: .indigo)
                    ScoreBarView(label: "Screen Time", score: latest.screenTimeScore, color: .orange)
                    ScoreBarView(label: "Mood", score: latest.moodScore, color: .yellow)
                    ScoreBarView(label: "Activity", score: latest.activityScore, color: .green)
                    ScoreBarView(label: "Workload", score: latest.workloadScore, color: .red)
                }
            } else {
                Text("No score data yet")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }

    // MARK: - Helpers

    private func colorForRisk(_ level: RiskLevel) -> Color {
        switch level {
        case .stable: return .green
        case .atRisk: return .orange
        case .burnoutLikely: return .red
        }
    }

    private func moodColor(_ mood: MoodLevel) -> Color {
        switch mood {
        case .great: return .green
        case .okay: return .mint
        case .flat: return .yellow
        case .stressed: return .orange
        case .exhausted: return .red
        }
    }

    private func shortDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "d"
        return formatter.string(from: date)
    }
}

// MARK: - Score Bar Component

struct ScoreBarView: View {
    let label: String
    let score: Double
    let color: Color

    var body: some View {
        HStack(spacing: 12) {
            Text(label)
                .font(.caption)
                .frame(width: 80, alignment: .trailing)

            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color.gray.opacity(0.2))

                    RoundedRectangle(cornerRadius: 4)
                        .fill(color)
                        .frame(width: geometry.size.width * min(score / 100, 1.0))
                }
            }
            .frame(height: 12)

            Text("\(Int(score))")
                .font(.caption)
                .fontWeight(.medium)
                .frame(width: 30, alignment: .trailing)
        }
    }
}

#Preview {
    TrendsView()
        .environmentObject(DataStore())
}
