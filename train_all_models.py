import subprocess

# List of training scripts
scripts = [
    "training/train_linear_regression.py",
    "training/train_random_forest.py",
    "training/train_gradient_boosting.py",
]

# Run each script
for script in scripts:
    print(f"Training with {script}...")
    subprocess.run(["python", script])

print("✅ All models have been trained.")
