import SwiftUI

/// Simple sparkline chart for trend visualization
struct MiniChartView: View {
    let dataPoints: [Double]
    let color: Color
    let height: CGFloat

    var body: some View {
        GeometryReader { geometry in
            if dataPoints.count >= 2 {
                let maxVal = dataPoints.max() ?? 1
                let minVal = dataPoints.min() ?? 0
                let range = max(maxVal - minVal, 1)

                Path { path in
                    let stepX = geometry.size.width / CGFloat(dataPoints.count - 1)

                    for (index, value) in dataPoints.enumerated() {
                        let x = CGFloat(index) * stepX
                        let normalizedY = (value - minVal) / range
                        let y = geometry.size.height * (1 - CGFloat(normalizedY))

                        if index == 0 {
                            path.move(to: CGPoint(x: x, y: y))
                        } else {
                            path.addLine(to: CGPoint(x: x, y: y))
                        }
                    }
                }
                .stroke(color, style: StrokeStyle(lineWidth: 2, lineCap: .round, lineJoin: .round))

                // Fill gradient under the line
                Path { path in
                    let stepX = geometry.size.width / CGFloat(dataPoints.count - 1)

                    path.move(to: CGPoint(x: 0, y: geometry.size.height))

                    for (index, value) in dataPoints.enumerated() {
                        let x = CGFloat(index) * stepX
                        let normalizedY = (value - minVal) / range
                        let y = geometry.size.height * (1 - CGFloat(normalizedY))
                        path.addLine(to: CGPoint(x: x, y: y))
                    }

                    path.addLine(to: CGPoint(x: geometry.size.width, y: geometry.size.height))
                    path.closeSubpath()
                }
                .fill(
                    LinearGradient(
                        gradient: Gradient(colors: [color.opacity(0.3), color.opacity(0.05)]),
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
            } else {
                Text("Not enough data")
                    .font(.caption2)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
            }
        }
        .frame(height: height)
    }
}

#Preview {
    MiniChartView(
        dataPoints: [30, 45, 38, 52, 62, 55, 48],
        color: .orange,
        height: 60
    )
    .padding()
}
