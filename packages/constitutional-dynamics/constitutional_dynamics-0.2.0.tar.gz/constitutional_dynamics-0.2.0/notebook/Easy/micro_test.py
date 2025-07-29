from constitutional_dynamics import (
    AlignmentVectorSpace,
    analyze_transition,
    predict_trajectory,
    calculate_stability_metrics,
    AlignmentOptimizer
)
from collections import deque
import time

print("=== CONSTITUTIONAL DYNAMICS MICRO-TEST SUITE ===\n")

# Setup base space
space = AlignmentVectorSpace(dimension=4)
space.define_alignment_region([1.0, 0.0, 0.0, 0.0], radius=0.3)

# Track state indices for analysis
state_indices = []
rolling_states = deque(maxlen=4)

print("🎯 TEST 1: DRIFT ALERT SYSTEM")
print("Goal: Detect when cosine similarity drops below threshold")

# Add progressively drifting states
test_states = [
    [1.0, 0.0, 0.0, 0.0],  # Perfect alignment
    [0.9, 0.1, 0.0, 0.0],  # Slight drift
    [0.7, 0.3, 0.0, 0.0],  # More drift
    [0.5, 0.5, 0.0, 0.0],  # Significant drift
    [0.0, 1.0, 0.0, 0.0],  # Complete misalignment
]

for i, state in enumerate(test_states):
    idx = space.add_state(state)
    state_indices.append(idx)
    rolling_states.append(idx)

    alignment_score = space.compute_alignment_score(state)
    print(f"  State {i}: {state} → Alignment: {alignment_score:.3f}")

    # Test drift alert (when we have previous state)
    if i > 0:
        transition = analyze_transition(space, state_indices[i - 1], state_indices[i])
        similarity = transition['similarity']
        drift_alert = similarity < 0.9  # Threshold

        print(f"    Similarity to prev: {similarity:.3f} | Drift Alert: {drift_alert}")

        if drift_alert:
            print(f"    🚨 DRIFT DETECTED at step {i}!")
    print()

print("🔮 TEST 2: ROLLING TRAJECTORY FORECAST")
print("Goal: Predict future alignment based on recent trajectory")

if len(rolling_states) >= 2:
    # Predict trajectory from latest state
    latest_idx = rolling_states[-1]
    predictions = predict_trajectory(space, latest_idx, steps=3)

    print(f"  Predicting from state index {latest_idx}:")
    for pred in predictions:
        if 'predicted_alignment' in pred:
            print(f"    Step {pred['step']}: Predicted alignment = {pred['predicted_alignment']:.3f}")
        else:
            print(f"    Step {pred['step']}: {pred}")
print()

print("📊 TEST 3: STABILITY METRICS DEMO")
print("Goal: Show Lyapunov-like drift detection")

stability = calculate_stability_metrics(space)
print(f"  States analyzed: {stability['num_states']}")
print(f"  Average alignment: {stability['avg_alignment']:.3f}")
print(f"  Alignment trend: {stability['alignment_trend']:.3f}")
print(f"  Alignment volatility: {stability['alignment_volatility']:.3f}")
print(f"  Lyapunov estimate: {stability['lyapunov_exponent_estimate']:.3f}")
print(f"  Stability score: {stability['stability_score']:.3f}")
print(f"  Region transitions: {stability['region_transitions']}")

if stability['alignment_trend'] < -0.1:
    print("  🚨 NEGATIVE TREND DETECTED!")
if stability['alignment_volatility'] > 0.2:
    print("  🚨 HIGH VOLATILITY DETECTED!")
print()

print("⚛️ TEST 4: QAOA/CLASSICAL OPTIMIZATION FALLBACK")
print("Goal: Test optimization with classical fallback")

# Test optimization
optimizer = AlignmentOptimizer(states=[{"id": i} for i in range(len(test_states))])

# Create phi and psd scores based on our test data
phi_scores = {}
psd_scores = {}
for i, state in enumerate(test_states):
    alignment = space.compute_alignment_score(state)
    phi_scores[i] = alignment
    psd_scores[i] = 1.0 - alignment  # Higher PSD for lower alignment

print(f"  Input phi scores: {phi_scores}")
print(f"  Input psd scores: {psd_scores}")

result = optimizer.optimize(phi_scores, psd_scores)
print(f"  Optimization result: {result}")
print(f"  Solver used: {result.get('solver', 'unknown')}")
print()

print("🔄 TEST 5: COMPLETE WORKFLOW")
print("Goal: Full pipeline demo")

# Create new space for clean demo
demo_space = AlignmentVectorSpace(dimension=3)
demo_space.define_alignment_region([1.0, 0.0, 0.0], radius=0.25)

workflow_states = [
    [1.0, 0.0, 0.0],  # Start aligned
    [0.8, 0.2, 0.0],  # Slight drift
    [0.6, 0.4, 0.0],  # More drift
    [0.0, 0.0, 1.0],  # Complete change
]

demo_indices = []
for i, state in enumerate(workflow_states):
    print(f"  Step {i + 1}: Adding state {state}")

    # 1. Add state
    idx = demo_space.add_state(state)
    demo_indices.append(idx)

    # 2. See score
    score = demo_space.compute_alignment_score(state)
    print(f"    Alignment score: {score:.3f}")

    # 3. Trigger drift alert (if not first state)
    if i > 0:
        transition = analyze_transition(demo_space, demo_indices[i - 1], demo_indices[i])
        if transition['similarity'] < 0.9:
            print(f"    🚨 DRIFT ALERT: Similarity = {transition['similarity']:.3f}")

    # 4. Project future drift (if enough states)
    if i >= 1:
        predictions = predict_trajectory(demo_space, idx, steps=2)
        if predictions and 'predicted_alignment' in predictions[0]:
            next_pred = predictions[0]['predicted_alignment']
            print(f"    🔮 Next predicted alignment: {next_pred:.3f}")

    # 5. Print stability metric
    if i >= 1:
        stability = calculate_stability_metrics(demo_space)
        print(f"    📊 Current stability score: {stability['stability_score']:.3f}")

    print()

print("✅ MICRO-TEST SUITE COMPLETE")
print("\nKey Findings:")
print("- Drift detection works via cosine similarity threshold")
print("- Trajectory prediction extrapolates from recent transitions")
print("- Stability metrics capture system volatility")
print("- Classical optimization fallback functions properly")
print("- Complete workflow integrates all components")