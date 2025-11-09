from __future__ import annotations
from typing import Optional, List, Tuple, Dict, Any

def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()

# FACT_RULES now maps matchers -> List[str] (multiple facts per species)
# Lexington/KY-friendly, nature-first: scents, wildlife, phenology, Indigenous/cultural notes.
FACT_RULES: List[Tuple[Dict[str, List[str]], List[str]]] = [
    # ——— Oaks & Maples ———
    ({'common': ['red oak'], 'latin': ['quercus rubra']}, [
        'Mature red oaks feed wildlife: blue jays cache their acorns, accidentally planting the next forest.',
        'Red oak leaf lobes are pointed; the buds are clustered at twig tips—look close in late winter.',
    ]),
    ({'common': ['willow oak'], 'latin': ['quercus phellos']}, [
        'Narrow, willow-like leaves make this oak easy to spot even from a distance.',
        'In autumn, willow oak crowns can glow warm yellow to russet, with leaves lingering late.',
    ]),
    ({'common': ['bur oak'], 'latin': ['quercus macrocarpa']}, [
        'Giant acorns wear shaggy caps—search beneath open-grown trees in late fall.',
        'Stout limbs and thick bark help bur oaks shrug off prairie winds and fire history.',
    ]),
    ({'common': ['pin oak'], 'latin': ['quercus palustris']}, [
        'Lower branches tend to angle downward while upper branches point up—classic “pin oak” posture.',
        'Prefers moist soils; look for pin oaks near low lawns and swales that hold spring water.',
    ]),
    ({'common': ['shumard oak'], 'latin': ['quercus shumardii']}, [
        'Autumn can set Shumard oaks ablaze with deep scarlet foliage.',
        'Shumard acorns feed squirrels and jays, keeping activity high on crisp mornings.',
    ]),
    ({'common': ['white oak'], 'latin': ['quercus alba']}, [
        'Leaves often turn wine-red and many persist into winter, rustling on cold days.',
        'Rounded lobes distinguish white oak leaves from the pointed lobes of red oaks.',
    ]),

    ({'common': ['red maple'], 'latin': ['acer rubrum']}, [
        'Color shows year-round: red twigs, buds, flowers, and samaras.',
        'Early spring flowers feed pollinators before many trees leaf out.',
    ]),
    ({'common': ['sugar maple'], 'latin': ['acer saccharum']}, [
        'Early spring sap rises with freeze–thaw cycles; fall brings vivid oranges and reds.',
        'Broad, classic lobes cast dense shade—great for reading on late summer afternoons.',
    ]),

    # ——— Elm cousin ———
    ({'common': ['sawleaf zelkova', 'zelkova'], 'latin': ['zelkova serrata']}, [
        'A hardy elm cousin with serrated leaves and fluted bark; often planted where elms once stood.',
        'Orange fall color can glow along streets on clear October days.',
    ]),

    # ——— Ash (including Blue Ash) ———
    ({'common': ['white ash'], 'latin': ['fraxinus americana']}, [
        'Opposite buds and leaf scars shaped like a smile—check winter twigs for the pattern.',
        'Watch for signs of emerald ash borer; woodpecker foraging can reveal early stress.',
    ]),
    ({'common': ['blue ash'], 'latin': ['fraxinus quadrangulata']}, [
        'Blue ash, native to the Bluegrass, helped give the region its name; twigs can tint blue in water.',
        'Square-ish twigs and stout branches create a bold winter silhouette.',
    ]),

    # ——— Flowering natives & regionals ———
    ({'common': ['eastern redbud', 'redbud'], 'latin': ['cercis canadensis']}, [
        'Blossoms can emerge on trunks and branches (cauliflory), painting bark with pink.',
        'Cherokee people traditionally steeped the blossoms as a gentle spring tea.',
        'Heart-shaped leaves make redbuds easy to ID after bloom.',
    ]),
    ({'common': ['southern magnolia'], 'latin': ['magnolia grandiflora']}, [
        'Large, citrus-sweet blossoms perfume warm spring evenings.',
        'Glossy evergreen leaves show bronze undersides—beautiful in winter light.',
    ]),
    # Magnolia cultivars common in landscapes (still nature-forward facts)
    ({'common': ['little gem magnolia', 'little gem'], 'latin': []}, [
        '“Little Gem” stays compact but keeps the grand, fragrant blooms of southern magnolia.',
        'Dense evergreen leaves make a year-round backdrop for nesting birds.',
    ]),
    ({'common': ['bracken’s brown beauty magnolia', "bracken's brown beauty", 'brackens brown beauty'], 'latin': []}, [
        '“Bracken’s Brown Beauty” shows deep bronze leaf undersides and abundant creamy blossoms.',
        'Cold-hardy for a southern magnolia type, keeping foliage attractive into winter.',
    ]),
    ({'common': ['crabapple'], 'latin': ['malus']}, [
        'Small fruits persist into winter and feed birds long after leaves drop.',
        'Spring bloom clouds trees in pinks and whites, drawing early pollinators.',
    ]),
    ({'common': ['goldenrain tree', 'golden rain'], 'latin': ['koelreuteria paniculata']}, [
        'Summer sprays of yellow flowers drift down like “golden rain.”',
        'Papery lantern pods follow the bloom—kids love to find them underfoot.',
    ]),
    ({'common': ['winter king hawthorn', 'hawthorn'], 'latin': ['crataegus viridis']}, [
        'Bright red berries hang through winter, a reliable cold-season food for birds.',
        'Fine thorns and silver-gray bark create intricate winter texture.',
    ]),

    # ——— Fruit / Nut natives ———
    ({'common': ['black walnut'], 'latin': ['juglans nigra']}, [
        'Roots release juglone, a natural compound that discourages some nearby plants.',
        'Green husks stain sidewalks and fingers dark—an autumn signature.',
    ]),
    ({'common': ['shagbark hickory'], 'latin': ['carya ovata']}, [
        'Long peeling bark plates give trunks a shaggy look.',
        'Loose bark can shelter overwintering insects and small creatures.',
    ]),
    ({'common': ['american persimmon', 'persimmon'], 'latin': ['diospyros virginiana']}, [
        'Fruits sweeten after frost—the “fruit of frost”—and feed wildlife into late fall.',
        'Check for flat, blocky bark plates and dangling fruits in November.',
    ]),
    ({'common': ['pawpaw'], 'latin': ['asimina triloba']}, [
        'Host plant for zebra swallowtail butterflies; caterpillars depend on pawpaw leaves.',
        'Maroon spring flowers hide beneath branches—easy to miss unless you look up close.',
    ]),

    # ——— Conifers / Evergreens ———
    ({'common': ['white pine'], 'latin': ['pinus strobus']}, [
        'Needles in clusters of five—think W-H-I-T-E to remember the count.',
        'On sunny winter days, needles release a subtle fresh scent.',
    ]),
    ({'common': ['eastern hemlock'], 'latin': ['tsuga canadensis']}, [
        'Flat sprays of soft needles and tiny pendant cones create cool, shaded microclimates.',
        'Hemlocks can host delicate moss gardens on their shaded roots and logs.',
    ]),
    ({'common': ['eastern red cedar', 'red cedar', 'juniper'], 'latin': ['juniperus virginiana']}, [
        'Crush the foliage for a clean, resinous scent.',
        'Cedar waxwings flock to the blue berry-like cones in winter.',
    ]),
    ({'common': ['norway spruce'], 'latin': ['picea abies']}, [
        'Long, hanging cones and drooping branchlets create a skirted silhouette.',
        'Wind in the long branches can make a low whisper you can hear at dusk.',
    ]),

    # ——— River / Bottomland ———
    ({'common': ['american sycamore', 'sycamore'], 'latin': ['platanus occidentalis']}, [
        'Mottled bark peels to white and green; in winter, trunks glow against gray skies.',
        'Hollows in old sycamores can shelter owls and wood ducks along waterways.',
    ]),

    # ——— Aromatic / Leaf-shape favorite ———
    ({'common': ['sassafras'], 'latin': ['sassafras albidum']}, [
        'Leaves come in three shapes—oval, mitten, and three-lobed—often on the same tree.',
        'Rub a leaf gently: a bright, spicy-citrus aroma lingers on your fingers.',
        'In autumn, sassafras can show a rainbow from yellow to crimson on the same branch.',
    ]),

    # ——— Hackberry (butterfly host) ———
    ({'common': ['hackberry'], 'latin': ['celtis occidentalis']}, [
        'Hackberry butterflies use it as a host; look for them sunning on warm paths.',
        'Warty bark ridges make trunks easy to ID by touch.',
    ]),

    # ——— Tulip poplar (tuliptree) ———
    ({'common': ['tulip poplar', 'tuliptree', 'yellow poplar'], 'latin': ['liriodendron tulipifera']}, [
        'Goblet-shaped flowers with orange bands attract pollinators in late spring.',
        'Leaves look like a cat’s face with pointed ears—distinct among broadleaf trees.',
        'Bees visit the nectar-rich blossoms, producing a dark, robust honey in season.',
    ]),

    # ——— Other / Unique ———
    ({'common': ['ginkgo', 'maidenhair'], 'latin': ['ginkgo biloba']}, [
        'Fan-shaped leaves often drop almost all at once, carpeting paths in gold.',
        'A living fossil: the species has ancient lineage stretching back to the time of dinosaurs.',
    ]),
    ({'common': ['osage orange', 'hedge apple'], 'latin': ['maclura pomifera']}, [
        'Bumpy green fruits fall in autumn; historic hedgerows made living fences across fields.',
        'Twisted, interlaced branches can form wildlife shelter during winter winds.',
    ]),
    ({'common': ['kentucky coffeetree', 'coffeetree'], 'latin': ['gymnocladus dioicus']}, [
        'Rattling pods persist on bare branches in winter.',
        'Coarse, bold twigs and large leaflets create a striking winter silhouette.',
    ]),
]

def get_tree_facts(common_name: Optional[str], latin_name: Optional[str]) -> Optional[List[str]]:
    """
    Returns a list of facts for the best-matching species (or None if unknown).
    Matching is OR: any common token in name OR any latin token.
    """
    c = _norm(common_name)
    l = _norm(latin_name)
    for (match, facts) in FACT_RULES:
        common_ok = any(token in c for token in match.get('common', [])) if c else False
        latin_ok  = any(token in l for token in match.get('latin', [])) if l else False
        if common_ok or latin_ok:
            return facts[:]  # return a shallow copy
    return None

# Backward-compat wrapper for legacy callers
def get_tree_fact(common_name: Optional[str], latin_name: Optional[str]) -> Optional[str]:
    facts = get_tree_facts(common_name, latin_name)
    return facts[0] if facts else None

# ----------------- Lightweight tests -----------------
def _run_tests():
    # Array-return behavior
    facts = get_tree_facts('Pawpaw', None)
    assert isinstance(facts, list) and len(facts) >= 2
    assert any('zebra swallowtail' in f for f in facts)

    # Latin fallback
    s_facts = get_tree_facts(None, 'Platanus occidentalis')
    assert s_facts and any('Mottled bark' in f or 'Mottled bark'.lower() in f.lower() for f in s_facts)

    # Cultivar matching (common-name only entries)
    mg = get_tree_facts('Little Gem Magnolia', None)
    assert mg and any('Little Gem' in f for f in mg)

    bb = get_tree_facts("Bracken's Brown Beauty", None)
    assert bb and any('Bracken’' in f or 'Bracken' in f for f in bb)

    # No utilitarian phrases
    banned = ['furniture', 'baseball', 'lumber', 'bats', 'tool handles']
    for species in [('White Ash', None), ('Red Oak', None), ('Black Walnut', None)]:
        fs = ' '.join(get_tree_facts(*species) or [])
        assert all(b not in fs.lower() for b in banned)

    # Legacy wrapper still returns a string (first fact)
    one = get_tree_fact('Ginkgo', None)
    assert isinstance(one, str) and 'fan-shaped' in one.lower()

    # Unknown → None
    assert get_tree_facts('Totally Unknown Tree', None) is None

if __name__ == '__main__':
    _run_tests()
    print('OK')
