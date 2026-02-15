import SwiftUI

/// Interventions library tab with categorized micro-interventions
struct InterventionsView: View {
    @State private var selectedCategory: InterventionCategory?

    private var filteredInterventions: [Intervention] {
        if let category = selectedCategory {
            return InterventionLibrary.all.filter { $0.category == category }
        }
        return InterventionLibrary.all
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(spacing: 20) {
                    // Category Filter
                    categoryFilter

                    // Interventions List
                    LazyVStack(spacing: 12) {
                        ForEach(filteredInterventions) { intervention in
                            NavigationLink(destination: InterventionDetailView(intervention: intervention)) {
                                InterventionCard(intervention: intervention)
                            }
                            .buttonStyle(.plain)
                        }
                    }
                }
                .padding()
            }
            .navigationTitle("Interventions")
        }
    }

    private var categoryFilter: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 8) {
                FilterChip(
                    title: "All",
                    isSelected: selectedCategory == nil,
                    action: { selectedCategory = nil }
                )

                ForEach(InterventionCategory.allCases, id: \.self) { category in
                    FilterChip(
                        title: category.rawValue,
                        isSelected: selectedCategory == category,
                        action: { selectedCategory = category }
                    )
                }
            }
        }
    }
}

// MARK: - Intervention Card

struct InterventionCard: View {
    let intervention: Intervention

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
        HStack(spacing: 16) {
            // Icon
            Image(systemName: intervention.iconName)
                .font(.title2)
                .foregroundColor(categoryColor)
                .frame(width: 44, height: 44)
                .background(categoryColor.opacity(0.15))
                .cornerRadius(10)

            // Content
            VStack(alignment: .leading, spacing: 4) {
                Text(intervention.title)
                    .font(.headline)
                    .foregroundColor(.primary)

                Text(intervention.description)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
            }

            Spacer()

            // Duration
            VStack(spacing: 2) {
                Text("\(intervention.durationMinutes)")
                    .font(.headline)
                    .foregroundColor(.primary)
                Text("min")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }

            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(12)
    }
}

// MARK: - Filter Chip

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Text(title)
                .font(.caption)
                .fontWeight(isSelected ? .semibold : .regular)
                .padding(.horizontal, 14)
                .padding(.vertical, 8)
                .background(isSelected ? Color.blue : Color(.systemGray5))
                .foregroundColor(isSelected ? .white : .primary)
                .cornerRadius(20)
        }
    }
}

#Preview {
    InterventionsView()
}
