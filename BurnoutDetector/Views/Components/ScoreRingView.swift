import SwiftUI

/// Circular progress ring displaying the burnout score
struct ScoreRingView: View {
    let score: Double
    let riskLevel: RiskLevel
    let size: CGFloat

    @State private var animatedProgress: Double = 0

    private var ringColor: Color {
        switch riskLevel {
        case .stable: return .green
        case .atRisk: return .yellow
        case .burnoutLikely: return .red
        }
    }

    var body: some View {
        ZStack {
            // Background ring
            Circle()
                .stroke(Color.gray.opacity(0.2), lineWidth: size * 0.08)

            // Progress ring
            Circle()
                .trim(from: 0, to: animatedProgress / 100)
                .stroke(
                    ringColor,
                    style: StrokeStyle(
                        lineWidth: size * 0.08,
                        lineCap: .round
                    )
                )
                .rotationEffect(.degrees(-90))

            // Score text
            VStack(spacing: 4) {
                Text("\(Int(score))")
                    .font(.system(size: size * 0.28, weight: .bold, design: .rounded))
                    .foregroundColor(.primary)

                Text(riskLevel.rawValue)
                    .font(.system(size: size * 0.09, weight: .medium))
                    .foregroundColor(ringColor)
            }
        }
        .frame(width: size, height: size)
        .onAppear {
            withAnimation(.easeOut(duration: 1.0)) {
                animatedProgress = score
            }
        }
        .onChange(of: score) { newValue in
            withAnimation(.easeOut(duration: 0.5)) {
                animatedProgress = newValue
            }
        }
    }
}

#Preview {
    VStack(spacing: 30) {
        ScoreRingView(score: 25, riskLevel: .stable, size: 200)
        ScoreRingView(score: 62, riskLevel: .atRisk, size: 200)
        ScoreRingView(score: 85, riskLevel: .burnoutLikely, size: 200)
    }
}
