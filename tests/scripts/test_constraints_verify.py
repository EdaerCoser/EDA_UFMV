"""
Quick verification script for constraint implementation
"""
import sys
sys.path.insert(0, '/c/Users/love_dog_home/Desktop/demo_rand')

from tests.test_api.helpers.scenario_generators import (
    create_medium_object,
    create_large_object,
    create_stress_object
)

def verify_medium_object():
    """Verify medium object constraints"""
    print("=" * 60)
    print("Testing MEDIUM object constraints (simple)")
    print("=" * 60)

    obj = create_medium_object(num_vars=15)

    # Check constraint exists
    assert hasattr(obj, 'simple_ordering'), "Missing simple_ordering constraint"

    # Test randomization
    failures = 0
    for i in range(10):
        success = obj.randomize()
        if not success:
            failures += 1
            print(f"  Iteration {i+1}: FAILED to randomize")
        else:
            # Verify constraint satisfaction
            if not (obj.var0 < obj.var1 and obj.var1 < obj.var2):
                failures += 1
                print(f"  Iteration {i+1}: Constraint violated")
            else:
                print(f"  Iteration {i+1}: OK (var0={obj.var0}, var1={obj.var1}, var2={obj.var2})")

    success_rate = (10 - failures) / 10 * 100
    print(f"\nSuccess Rate: {success_rate:.0f}%")
    return failures == 0

def verify_large_object():
    """Verify large object constraints"""
    print("\n" + "=" * 60)
    print("Testing LARGE object constraints (medium)")
    print("=" * 60)

    obj = create_large_object(num_vars=30)

    # Check constraints exist
    assert hasattr(obj, 'sum_constraint'), "Missing sum_constraint"
    assert hasattr(obj, 'range_constraint'), "Missing range_constraint"

    # Test randomization
    failures = 0
    for i in range(10):
        success = obj.randomize()
        if not success:
            failures += 1
            print(f"  Iteration {i+1}: FAILED to randomize")
        else:
            # Verify constraint satisfaction
            sum_ok = (obj.var0 + obj.var1 + obj.var2 + obj.var3) < 500
            range_ok = 50 <= obj.var5 <= 150

            if not (sum_ok and range_ok):
                failures += 1
                print(f"  Iteration {i+1}: Constraint violated (sum={sum_ok}, range={range_ok})")
            else:
                total = obj.var0 + obj.var1 + obj.var2 + obj.var3
                print(f"  Iteration {i+1}: OK (sum={total}, var5={obj.var5})")

    success_rate = (10 - failures) / 10 * 100
    print(f"\nSuccess Rate: {success_rate:.0f}%")
    return failures == 0

def verify_stress_object():
    """Verify stress object constraints"""
    print("\n" + "=" * 60)
    print("Testing STRESS object constraints (complex)")
    print("=" * 60)

    obj = create_stress_object(num_vars=50)

    # Check constraints exist
    assert hasattr(obj, 'complex_ordering'), "Missing complex_ordering"
    assert hasattr(obj, 'weighted_sum'), "Missing weighted_sum"
    assert hasattr(obj, 'range_limits'), "Missing range_limits"
    assert hasattr(obj, 'logical_combination'), "Missing logical_combination"

    # Test randomization
    failures = 0
    for i in range(10):
        success = obj.randomize()
        if not success:
            failures += 1
            print(f"  Iteration {i+1}: FAILED to randomize")
        else:
            # Verify all constraints
            ordering_ok = obj.var0 < obj.var1 < obj.var2 < obj.var3
            weighted_ok = (obj.var0 * 2 + obj.var1 * 3 + obj.var2) < 400
            range_ok = (20 <= obj.var4 <= 100) and (30 <= obj.var5 <= 120)
            logical_ok = (obj.var6 + obj.var7 < 200) and (obj.var8 > obj.var9)

            if not (ordering_ok and weighted_ok and range_ok and logical_ok):
                failures += 1
                print(f"  Iteration {i+1}: Constraints violated")
                print(f"    ordering={ordering_ok}, weighted={weighted_ok}, range={range_ok}, logical={logical_ok}")
            else:
                weighted = obj.var0 * 2 + obj.var1 * 3 + obj.var2
                print(f"  Iteration {i+1}: OK (weighted_sum={weighted})")

    success_rate = (10 - failures) / 10 * 100
    print(f"\nSuccess Rate: {success_rate:.0f}%")
    return failures == 0

if __name__ == "__main__":
    try:
        medium_ok = verify_medium_object()
        large_ok = verify_large_object()
        stress_ok = verify_stress_object()

        print("\n" + "=" * 60)
        print("FINAL RESULTS")
        print("=" * 60)
        print(f"Medium object (simple constraints):    {'✅ PASS' if medium_ok else '❌ FAIL'}")
        print(f"Large object (medium constraints):     {'✅ PASS' if large_ok else '❌ FAIL'}")
        print(f"Stress object (complex constraints):   {'✅ PASS' if stress_ok else '❌ FAIL'}")
        print("=" * 60)

        if medium_ok and large_ok and stress_ok:
            print("\n✅ ALL CONSTRAINTS VERIFIED - SPEC COMPLIANT")
            sys.exit(0)
        else:
            print("\n❌ SOME CONSTRAINTS FAILED - SPEC ISSUES REMAIN")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
