# A worked example — one direction, from idea to killed, in one afternoon

Everything below is a real sequence you can type. It ends in a NO-GO, which is
the outcome this pipeline exists to produce cheaply and the one no other
walkthrough shows you.

The made-up direction: *"a learned module that repairs the connectivity of
segmented structures should beat the usual post-processing."*

---

## 1. Is it already done? (twenty minutes)

```console
$ groundwork lit occupancy "learned topology repair segmentation connectivity" -n 8
 1. 2023  Topology-preserving loss for tubular structure segmentation
 ...
# backends: arxiv: ok, openalex: ok, semanticscholar: ok
```

Read the closest two or three. Not the abstracts — a verdict of "already
occupied" requires reading the thing that occupies it. And check your own prior
output first: a "new paper" has turned out to be a table in its authors' own
supplementary material.

If the primary index does not answer, **there is no verdict**:

```
# ====================================================================
#  NO VERDICT AVAILABLE. The primary index did not answer, so this is
#  a preprint-only search.
# ====================================================================
```

A spent daily quota and an empty literature look identical, and the answer a
spent quota gives is *"nobody has done this"*.

---

## 2. The four numbers (one afternoon)

Not the proposed method. Four measurements on the same split:

| | what you run | result |
|---|---|---|
| **baseline** | the standard post-processing, **tuned as hard as you would tune your method** | 0.812 |
| **oracle** | repair with access to the ground-truth topology | 0.830 |
| **se** | standard error of a difference on this split | 0.019 |
| **random** | repair at randomly chosen locations | 0.805 |

```console
$ groundwork gate --baseline 0.812 --oracle 0.830 --se 0.019 --random 0.805

  headroom            +0.0180  (oracle 0.8300 - baseline 0.8120)
  one standard error  0.0190
  headroom in SEs     0.95
  smallest detectable 0.0532  (80% power, two-sided 0.05)

NO-GO.
  * Headroom is 0.95 SE, under the 2 SE this gate requires. Even a method that
    captured the entire gap would not separate from the baseline on this split.
  * A random arm scores 0.8050 against a baseline of 0.8120. Whatever this task
    measures, it is not something a learned policy has yet been shown to need.
```

**Two independent reasons, before any model was trained.**

The second one is the uncomfortable one and it is not hypothetical: in one real
programme a random assignment policy improved the headline metric by 25.9% and
beat every learned method it was compared against.

### The mistake this gate exists to prevent

If you had compared the oracle against your **own untuned** baseline, you would
have seen apparent headroom and started. That happened: a project measured its
ceiling on day one, saw 2.7× of headroom, passed, and ended two weeks later with
a gain of **−0.0024** once the baseline was given the same tuning budget. Six
further adversarial checks in between, and **not one asked whether the control
had been tuned**.

---

## 3. Record the death (two minutes)

```console
$ groundwork ledger kill --id topology-repair --cause ceiling-too-low \
    --what "an oracle with ground-truth topology beat the tuned baseline by 0.95 SE" \
    --settled-by "oracle + tuned baseline + random arm, one afternoon" \
    --reopen-if "a split large enough to resolve 2 points, or a metric that is not inflatable by doing more"

recorded topology-repair as ceiling-too-low (The ceiling was never high enough)
archive now holds 1 killed direction(s)
```

This is the step people skip, and it is the one that pays. A direction killed
silently gets re-proposed in four months by somebody with the same good taste
that proposed it the first time — often you — and they will not find your
reasoning because you did not write it down.

`--reopen-if` matters too. Several directions killed for lack of compute were
genuinely revivable the moment a bigger machine was free, and the ones that said
so got revived.

---

## 4. If it had passed

```bash
# seal the plan before generating anything
groundwork prereg new prereg/PREREG_run1.md --title "run 1"
# ... fill all six sections, including what gets written if it comes out the other way
groundwork prereg seal prereg/PREREG_run1.md
git add prereg/ && git commit -m "Pre-register run 1"     # BEFORE the run

# find capacity that is actually free, and plan shards
groundwork cluster survey --nodes gpu01 gpu02 gpu03
groundwork cluster plan --nodes gpu01 gpu03 --need-gb 20 --shards 4 \
    --command 'python eval.py'

# ... run ...

# then prove the plan predated the results
groundwork prereg verify prereg/PREREG_run1.md --results results/metrics.json
```

`verify` checks the seal, checks every section is filled, and checks **with git**
that the pre-registration was committed before the results it governs:

```
FAIL results.json was committed BEFORE the pre-registration was committed.
     A pre-registration written after its results is a write-up.
```

Then the claims:

```bash
pip install doubleblind-audit     # the command is still `doubleblind`
doubleblind trace README.md --data results/ --derive 'python scripts/metrics.py'
doubleblind review README.md --data results/ --agent codex     # a different model
doubleblind render figures/main.py                             # what a reader sees
```

---

## The arithmetic

| step | cost | what it can save |
|---|---|---|
| occupancy | 20 min | weeks |
| the four numbers | one afternoon | weeks to months |
| recording the death | 2 min | the same afternoon, twice |
| a sealed pre-registration | 30 min | a result nobody can check, including you |

The whole gate costs less than the first day of the work it prevents. That is
the entire argument.
