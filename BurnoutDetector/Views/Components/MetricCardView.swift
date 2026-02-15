import SwiftUI

/// Card showing a single metric with trend indicator
struct MetricCardView: View {
    let title: String
    let value: String
    let change: String
    let direction: TrendDirection
    let iconName: String

    private var changeColor: Color {
        switch direction {
        case .up: return title == "Steps" || title == "Activity" ? .green : .red
        case .down: return title == "Steps" || title == "Activity" ? .red : .green
        case .stable: return .secondary
        }
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: iconName)
                    .font(.system(size: 14))
                    .foregroundColor(.secondary)
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Text(value)
                .font(.system(size: 20, weight: .semibold, design: .rounded))
                .foregroundColor(.primary)

            HStack(spacing: 4) {
                Text(direction.arrow)
                    .font(.caption)
                Text(change)
                    .font(.caption)
            }
            .foregroundColor(changeColor)
        }
        .padding()
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

#Preview {
    HStack {
        MetricCardView(
            title: "Sleep",
            value: "6.2h",
            change: "12%",
            direction: .down,
            iconName: "moon.fill"
        )
        MetricCardView(
            title: "Screen Time",
            value: "9.4h",
            change: "18%",
            direction: .up,
            iconName: "iphone"
        )
    }
    .padding()
}
