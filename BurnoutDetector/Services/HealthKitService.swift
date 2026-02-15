import Foundation
import HealthKit
import Combine

/// Service for reading health data from HealthKit (sleep, steps, activity)
final class HealthKitService: ObservableObject {
    private let healthStore = HKHealthStore()
    @Published var isAuthorized = false
    @Published var lastError: String?

    // MARK: - Authorization

    /// Types we read from HealthKit
    private var readTypes: Set<HKObjectType> {
        guard let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis),
              let stepType = HKObjectType.quantityType(forIdentifier: .stepCount),
              let activeEnergyType = HKObjectType.quantityType(forIdentifier: .activeEnergyBurned),
              let exerciseTimeType = HKObjectType.quantityType(forIdentifier: .appleExerciseTime)
        else {
            return []
        }
        return [sleepType, stepType, activeEnergyType, exerciseTimeType]
    }

    func requestAuthorization() async -> Bool {
        guard HKHealthStore.isHealthDataAvailable() else {
            await MainActor.run { self.lastError = "HealthKit is not available on this device" }
            return false
        }

        do {
            try await healthStore.requestAuthorization(toShare: [], read: readTypes)
            await MainActor.run { self.isAuthorized = true }
            return true
        } catch {
            await MainActor.run { self.lastError = error.localizedDescription }
            return false
        }
    }

    // MARK: - Sleep Data

    /// Fetch total sleep hours for a given date
    func fetchSleepHours(for date: Date) async -> Double? {
        guard let sleepType = HKObjectType.categoryType(forIdentifier: .sleepAnalysis) else {
            return nil
        }

        let startOfDay = Calendar.current.startOfDay(for: date)
        let endOfDay = Calendar.current.date(byAdding: .day, value: 1, to: startOfDay)!

        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: endOfDay,
            options: .strictStartDate
        )

        return await withCheckedContinuation { continuation in
            let query = HKSampleQuery(
                sampleType: sleepType,
                predicate: predicate,
                limit: HKObjectQueryNoLimit,
                sortDescriptors: nil
            ) { _, samples, error in
                guard let samples = samples as? [HKCategorySample], error == nil else {
                    continuation.resume(returning: nil)
                    return
                }

                // Filter for asleep states (not inBed)
                let asleepSamples = samples.filter { sample in
                    sample.value == HKCategoryValueSleepAnalysis.asleepCore.rawValue ||
                    sample.value == HKCategoryValueSleepAnalysis.asleepDeep.rawValue ||
                    sample.value == HKCategoryValueSleepAnalysis.asleepREM.rawValue ||
                    sample.value == HKCategoryValueSleepAnalysis.asleepUnspecified.rawValue
                }

                let totalSeconds = asleepSamples.reduce(0.0) { total, sample in
                    total + sample.endDate.timeIntervalSince(sample.startDate)
                }

                continuation.resume(returning: totalSeconds / 3600.0)
            }
            healthStore.execute(query)
        }
    }

    /// Calculate sleep consistency over the last N days (0.0–1.0)
    func fetchSleepConsistency(days: Int = 7) async -> Double? {
        var sleepHoursArray: [Double] = []

        for dayOffset in 0..<days {
            guard let date = Calendar.current.date(byAdding: .day, value: -dayOffset, to: Date()) else {
                continue
            }
            if let hours = await fetchSleepHours(for: date) {
                sleepHoursArray.append(hours)
            }
        }

        guard sleepHoursArray.count >= 3 else { return nil }

        let mean = sleepHoursArray.reduce(0, +) / Double(sleepHoursArray.count)
        guard mean > 0 else { return 0 }

        let variance = sleepHoursArray.reduce(0) { $0 + pow($1 - mean, 2) } / Double(sleepHoursArray.count)
        let stdDev = sqrt(variance)

        // Lower std dev = higher consistency; normalize to 0–1
        // A std dev of 0 = perfect consistency (1.0)
        // A std dev of 3+ hours = very inconsistent (near 0.0)
        let consistency = max(0, 1.0 - (stdDev / 3.0))
        return consistency
    }

    // MARK: - Steps

    /// Fetch step count for a given date
    func fetchStepCount(for date: Date) async -> Int? {
        guard let stepType = HKQuantityType.quantityType(forIdentifier: .stepCount) else {
            return nil
        }

        let startOfDay = Calendar.current.startOfDay(for: date)
        let endOfDay = Calendar.current.date(byAdding: .day, value: 1, to: startOfDay)!

        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: endOfDay,
            options: .strictStartDate
        )

        return await withCheckedContinuation { continuation in
            let query = HKStatisticsQuery(
                quantityType: stepType,
                quantitySamplePredicate: predicate,
                options: .cumulativeSum
            ) { _, result, error in
                guard let result = result, let sum = result.sumQuantity(), error == nil else {
                    continuation.resume(returning: nil)
                    return
                }
                let steps = Int(sum.doubleValue(for: HKUnit.count()))
                continuation.resume(returning: steps)
            }
            healthStore.execute(query)
        }
    }

    // MARK: - Active Minutes

    /// Fetch exercise/active minutes for a given date
    func fetchActiveMinutes(for date: Date) async -> Double? {
        guard let exerciseType = HKQuantityType.quantityType(forIdentifier: .appleExerciseTime) else {
            return nil
        }

        let startOfDay = Calendar.current.startOfDay(for: date)
        let endOfDay = Calendar.current.date(byAdding: .day, value: 1, to: startOfDay)!

        let predicate = HKQuery.predicateForSamples(
            withStart: startOfDay,
            end: endOfDay,
            options: .strictStartDate
        )

        return await withCheckedContinuation { continuation in
            let query = HKStatisticsQuery(
                quantityType: exerciseType,
                quantitySamplePredicate: predicate,
                options: .cumulativeSum
            ) { _, result, error in
                guard let result = result, let sum = result.sumQuantity(), error == nil else {
                    continuation.resume(returning: nil)
                    return
                }
                let minutes = sum.doubleValue(for: HKUnit.minute())
                continuation.resume(returning: minutes)
            }
            healthStore.execute(query)
        }
    }

    // MARK: - Aggregate Daily Metrics

    /// Fetch all health metrics for a specific date
    func fetchDailyMetrics(for date: Date) async -> HealthMetrics {
        async let sleep = fetchSleepHours(for: date)
        async let consistency = fetchSleepConsistency()
        async let steps = fetchStepCount(for: date)
        async let active = fetchActiveMinutes(for: date)

        return HealthMetrics(
            date: date,
            sleepHours: await sleep,
            sleepConsistency: await consistency,
            stepCount: await steps,
            activeMinutes: await active
        )
    }

    /// Fetch metrics for the last N days
    func fetchMetricsHistory(days: Int = 7) async -> [HealthMetrics] {
        var metrics: [HealthMetrics] = []
        for dayOffset in 0..<days {
            guard let date = Calendar.current.date(byAdding: .day, value: -dayOffset, to: Date()) else {
                continue
            }
            let daily = await fetchDailyMetrics(for: date)
            metrics.append(daily)
        }
        return metrics.reversed() // oldest first
    }
}
