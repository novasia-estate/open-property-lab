using NovAsia.ServiceChargeAllocation;
int checks=0;
void Check(bool result,string name) { if(!result) throw new Exception(name); checks++; }
void Reject(Action action,string name) { try { action(); } catch(ArgumentException) { checks++; return; } throw new Exception("Accepted: "+name); }
var eq=new[]{new AllocationWeight("b",1),new AllocationWeight("a",1),new AllocationWeight("c",1)};
var a=Allocator.Allocate(1001,"USD",eq);
Check(a.Shares.Select(s=>s.MinorUnits).SequenceEqual(new long[]{334,334,333}),"Fixed independent equal thirds");
Check(a.Shares.SequenceEqual(Allocator.Allocate(1001,"USD",eq.Reverse()).Shares),"Input order invariant");
Check(Allocator.Allocate(7,"JPY",new[]{new AllocationWeight("x",0),new AllocationWeight("y",1)}).Shares[0].MinorUnits==0,"Zero weight gets zero");
Check(Allocator.Allocate(0,"USD",eq).Shares.All(s=>s.MinorUnits==0),"Zero total");
Check(Allocator.Allocate(long.MaxValue,"USD",new[]{new AllocationWeight("x",decimal.MaxValue),new AllocationWeight("y",decimal.MaxValue)}).Shares.Sum(s=>s.MinorUnits)==long.MaxValue,"BigInteger avoids multiplication overflow");
Check(Allocator.Allocate(3,"USD",new[]{new AllocationWeight("a",0.1m),new AllocationWeight("b",0.2m)}).Shares.Select(s=>s.MinorUnits).SequenceEqual(new long[]{1,2}),"Decimal exactness");
Reject(()=>Allocator.Allocate(-1,"USD",eq),"negative total");Reject(()=>Allocator.Allocate(1,"usd",eq),"currency syntax");
Reject(()=>Allocator.Allocate(1,"USD",Array.Empty<AllocationWeight>()),"empty");
Reject(()=>Allocator.Allocate(1,"USD",new[]{new AllocationWeight("a",0)}),"all zero");
Reject(()=>Allocator.Allocate(1,"USD",new[]{new AllocationWeight("a",1),new AllocationWeight("a",2)}),"duplicate IDs");
Reject(()=>Allocator.Allocate(1,"USD",new[]{new AllocationWeight("a",-1)}),"negative weight");
Check(Allocator.OverlapDays(new(2024,2,1),new(2024,3,1),new(2024,2,10),new(2024,3,3))==20,"Leap February overlap");
Check(Allocator.OverlapDays(new(2024,2,1),new(2024,3,1),new(2024,3,1),new(2024,4,1))==0,"Adjacent periods");
for(int n=1;n<=30;n++) {
 var w=Enumerable.Range(0,n).Select(i=>new AllocationWeight(i.ToString("D2"),(i+1)*0.17m)).ToArray();
 var result=Allocator.Allocate(10000+n,"USD",w);
 Check(result.Shares.Sum(s=>s.MinorUnits)==10000+n,"Reconciles"+n);
 Check(result.Shares.All(s=>s.MinorUnits>=0),"Nonnegative"+n);
}
Console.WriteLine($"PASS {checks} allocation checks");
