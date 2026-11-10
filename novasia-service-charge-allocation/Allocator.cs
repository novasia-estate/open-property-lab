using System.Numerics;
namespace NovAsia.ServiceChargeAllocation;

/// <summary>Caller-defined nonnegative weight, not a statutory entitlement.</summary>
public sealed record AllocationWeight(string Id, decimal Weight);
/// <summary>Rounded amount plus the exact quota fraction in minor currency units.</summary>
public sealed record AllocatedShare(string Id, long MinorUnits, string QuotaNumerator, string QuotaDenominator);
public sealed record AllocationResult(string Currency, long TotalMinorUnits, IReadOnlyList<AllocatedShare> Shares);

public static class Allocator
{
    /// <summary>Distributes every minor unit by largest remainders. Equal remainders use ordinal ID order.</summary>
    /// <remarks>Integer inputs have caller-defined currency precision. No FX or fee/ownership rules are inferred.</remarks>
    public static AllocationResult Allocate(long totalMinorUnits, string currency, IEnumerable<AllocationWeight> weights)
    {
        ArgumentNullException.ThrowIfNull(weights);
        if (totalMinorUnits < 0) throw new ArgumentOutOfRangeException(nameof(totalMinorUnits));
        if (currency is null || currency.Length != 3 || currency.Any(c => c is < 'A' or > 'Z'))
            throw new ArgumentException("Supply three uppercase currency letters; no currency membership/precision is inferred.");
        var rows = weights.ToArray();
        if (rows.Length is < 1 or > 10000) throw new ArgumentException("Require1–10000 weights.");
        if (rows.Any(r => r is null || string.IsNullOrWhiteSpace(r.Id) || r.Id.Length > 128 || r.Id.Any(char.IsControl) || r.Weight < 0))
            throw new ArgumentException("Every weight needs a printable ID and nonnegative decimal weight.");
        if (rows.Select(r => r.Id).Distinct(StringComparer.Ordinal).Count() != rows.Length) throw new ArgumentException("Duplicate IDs.");
        var parts = rows.Select(r => DecimalParts(r.Weight)).ToArray();
        int scale = parts.Max(p => p.Scale);
        var units = parts.Select(p => p.Unscaled * BigInteger.Pow(10, scale-p.Scale)).ToArray();
        BigInteger denominator = units.Aggregate(BigInteger.Zero, (a,b) => a+b);
        if (denominator.IsZero) throw new ArgumentException("At least one positive weight is required.");
        var quotas = units.Select(w => w * totalMinorUnits).ToArray();
        var amounts = quotas.Select(q => (long)(q / denominator)).ToArray();
        long residual = totalMinorUnits - amounts.Sum();
        var order = Enumerable.Range(0, rows.Length)
            .OrderByDescending(i => quotas[i] % denominator).ThenBy(i => rows[i].Id, StringComparer.Ordinal).ToArray();
        for (int i=0; i<residual; i++) amounts[order[i]]++;
        var result = rows.Select((r,i) => new AllocatedShare(r.Id, amounts[i], quotas[i].ToString(), denominator.ToString()))
            .OrderBy(r => r.Id, StringComparer.Ordinal).ToArray();
        return new AllocationResult(currency, totalMinorUnits, Array.AsReadOnly(result));
    }

    /// <summary>Returns overlap days for half-open date ranges [start,end). Adjacent periods do not overlap.</summary>
    public static int OverlapDays(DateOnly periodStart, DateOnly periodEnd, DateOnly ownerStart, DateOnly ownerEnd)
    {
        if (periodEnd < periodStart || ownerEnd < ownerStart) throw new ArgumentException("Reversed period.");
        var from = periodStart > ownerStart ? periodStart : ownerStart;
        var to = periodEnd < ownerEnd ? periodEnd : ownerEnd;
        return Math.Max(0, to.DayNumber-from.DayNumber);
    }

    private static (BigInteger Unscaled,int Scale) DecimalParts(decimal value)
    {
        var bits=decimal.GetBits(value);
        return (new BigInteger((uint)bits[0]) + (new BigInteger((uint)bits[1]) << 32) + (new BigInteger((uint)bits[2]) << 64), (bits[3] >> 16) & 255);
    }
}
