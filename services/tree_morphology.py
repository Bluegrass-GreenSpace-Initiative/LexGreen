from __future__ import annotations
from typing import Optional, List, Tuple, Dict


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


# Rules are lists of (matchers, description). A match succeeds if any token in
# 'common' OR any token in 'latin' is present in the corresponding string.
# Keep descriptions short, vivid, and field-usable.
LEAF_RULES: List[Tuple[Dict[str, List[str]], str]] = [
    # Oaks (Quercus)
    ({'common': ['red oak'], 'latin': ['quercus rubra']},
     "Pointed lobes with tiny bristle tips (7–11) — like little antennae!"),
    ({'common': ['white oak'], 'latin': ['quercus alba']},
     "Rounded, fingerlike lobes (7–9), no bristles — smooth and classic."),
    ({'common': ['pin oak'], 'latin': ['quercus palustris']},
     "Deeply cut leaves with 5–7 pointed lobes and broad U-shaped sinuses; tiny tufts in vein angles underneath."),
    ({'common': ['bur oak'], 'latin': ['quercus macrocarpa']},
     "Huge leaf with a ‘waist’ — looks like it’s wearing a belt!"),
    ({'common': ['willow oak'], 'latin': ['quercus phellos']},
     "Long, narrow, willow-like leaves with no lobes — oak that breaks the rules!"),
    ({'common': ['shumard oak'], 'latin': ['quercus shumardii']},
     "7–9 pointed lobes with deep sinuses — bold, dramatic silhouette."),
    ({'common': ['chestnut oak', 'basket oak'], 'latin': ['quercus montana', 'quercus prinus']},
     "Large leaves with rounded teeth (not lobes) — a giant’s comb with wavy margins."),
    ({'common': ['scarlet oak'], 'latin': ['quercus coccinea']},
     "Deeply cut lobes with C-shaped sinuses — extremely sculpted look."),
    ({'common': ['swamp white oak'], 'latin': ['quercus bicolor']},
     "Rounded lobes on the outer half; two-toned — dark green above, silvery-white below."),
    ({'common': ['chinquapin oak'], 'latin': ['quercus muehlenbergii']},
     "Coarsely toothed margins like shark teeth — not lobed; shiny yellow-green."),
    ({'common': ['shingle oak'], 'latin': ['quercus imbricaria']},
     "Simple, unlobed, laurel-like leaves — an oak with smooth edges!"),
    ({'common': ['sawtooth oak'], 'latin': ['quercus acutissima']},
     "Long, narrow leaf with bristle-tipped teeth along the edge — like a saw blade!"),
    ({'common': ['english oak'], 'latin': ['quercus robur']},
      "Small, rounded lobes; leaves are nearly sessile (very short stems) — storybook oak vibe."),
    ({'common': ['cherrybark oak'], 'latin': ['quercus pagoda']},
     "5–11 pointed lobes; overall leaf outline can look pyramid-shaped (pagoda-like)."),

    # Maples (Acer)
    ({'common': ['sugar maple'], 'latin': ['acer saccharum']},
     "Classic 5-lobed maple leaf with smooth U-shaped notches between lobes."),
    ({'common': ['red maple'], 'latin': ['acer rubrum']},
     "3–5 lobes with toothed edges and V-shaped notches — smaller than sugar maple."),
    ({'common': ['silver maple'], 'latin': ['acer saccharinum']},
     "Deeply cut 5 lobes with silvery-white undersides — trees shimmer in a breeze."),
    ({'common': ['black maple'], 'latin': ['acer nigrum']},
     "Like sugar maple but with 3 main lobes (sometimes 5) and droopy, slightly fuzzy leaves."),

    # Walnuts & Hickories
    ({'common': ['black walnut'], 'latin': ['juglans nigra']},
     "Compound leaves with 15–23 narrow leaflets; crush a leaflet for a spicy-sweet scent."),
    ({'common': ['shagbark hickory'], 'latin': ['carya ovata']},
     "Compound with 5 (sometimes 7) leaflets — the end leaflet is much larger."),
    ({'common': ['pecan'], 'latin': ['carya illinoinensis']},
     "Compound with 9–17 curved, lance-shaped leaflets — classic pecan look."),

    # Ash (Fraxinus)
    ({'common': ['white ash'], 'latin': ['fraxinus americana']},
     "Compound leaves with 5–9 (usually 7) smooth-edged leaflets; opposite branching is a giveaway."),
    ({'common': ['blue ash'], 'latin': ['fraxinus quadrangulata']},
     "Compound with 7–11 sharply toothed leaflets; twigs are square in cross-section!"),

    # Magnolias
    ({'common': ['southern magnolia'], 'latin': ['magnolia grandiflora']},
     "Huge, glossy evergreen ovals (5–10\") with rusty-brown fuzzy undersides."),
    ({'common': ['saucer magnolia'], 'latin': ['magnolia x soulangeana']},
     "Large, soft green, oval leaves (deciduous); blooms before leaves in spring."),

    # Sycamore / Plane
    ({'common': ['american sycamore', 'sycamore'], 'latin': ['platanus occidentalis']},
     "Large, maple-like leaves with 3–5 shallow lobes — often as wide as your hand."),
    ({'common': ['london plane'], 'latin': ['platanus x acerifolia']},
     "Maple-like leaves similar to sycamore but typically a bit smaller."),

    # Unique & Exotic
    ({'common': ['ginkgo', 'maidenhair'], 'latin': ['ginkgo biloba']},
     "Fan-shaped leaf with a central notch — like a duck’s foot or a geisha’s fan."),
    ({'common': ['eastern redbud', 'redbud'], 'latin': ['cercis canadensis']},
     "Perfect heart-shaped leaves — Valentine vibes on a branch!"),
    ({'common': ['tulip tree', 'tuliptree', 'tulip poplar'], 'latin': ['liriodendron tulipifera']},
     "4 lobes with a squared-off tip — looks like a tulip or a cat face."),
    ({'common': ['yellowwood'], 'latin': ['cladrastis kentukea']},
     "Compound leaves with 7–11 oval leaflets, alternately arranged — rare among compound leaves."),
    ({'common': ['goldenrain', 'goldenrain tree', 'golden rain'], 'latin': ['koelreuteria paniculata']},
     "Compound with irregularly toothed and lobed leaflets — fancy, lacy texture."),
    ({'common': ['japanese pagoda', 'pagoda tree'], 'latin': ['styphnolobium japonicum']},
     "Compound with 7–17 small oval leaflets — elegant and airy."),
    ({'common': ['sawleaf zelkova', 'zelkova'], 'latin': ['zelkova serrata']},
     "Elm-like with crisp, sharply serrated edges — tiny saw teeth you can see."),
    ({'common': ['kentucky coffeetree', 'coffeetree'], 'latin': ['gymnocladus dioicus']},
     "Huge doubly compound leaves (leaflets on leaflets!) — bold and tropical-looking."),
    ({'common': ['amur corktree', 'corktree'], 'latin': ['phellodendron amurense']},
     "Compound with 5–13 aromatic leaflets; crush to release a citrusy scent."),
    ({'common': ['american hornbeam', 'musclewood'], 'latin': ['carpinus caroliniana']},
     "Oval leaves with prominent, parallel veins and doubly toothed margins."),

    # Elms
    ({'common': ['field elm'], 'latin': ['ulmus minor']},
     "Small oval leaves with doubly-toothed edges and a lopsided base; upper surface rough."),
    ({'common': ['american elm'], 'latin': ['ulmus americana']},
     "Oval, doubly toothed, uneven base — a larger, classic elm leaf."),
    ({'common': ['slippery elm'], 'latin': ['ulmus rubra']},
     "Large leaves with very rough (sandpapery) upper surface and uneven base."),
    ({'common': ['chinese elm'], 'latin': ['ulmus parvifolia']},
     "Small leaves with simple teeth and a more symmetrical base than other elms."),

    # Lindens / Basswoods
    ({'common': ['little-leaf linden', 'little leaf linden'], 'latin': ['tilia cordata']},
     "Small heart-shaped leaves with fine teeth and pointed tips — dark green and shiny."),
    ({'common': ['american linden', 'basswood'], 'latin': ['tilia americana']},
     "Larger heart-shaped leaves (to ~6\") with coarser teeth — soft wood favorite for carving."),

    # Beeches
    ({'common': ['american beech'], 'latin': ['fagus grandifolia']},
     "Thin, oval leaves with straight parallel veins and coarse teeth — papery feel."),
    ({'common': ['european beech'], 'latin': ['fagus sylvatica']},
     "Similar to American beech but darker, glossier, with subtly wavy edges."),

    # Conifers
    ({'common': ['white pine'], 'latin': ['pinus strobus']},
     "Soft needles in bundles of 5 — remember ‘white’ has five letters!"),
    ({'common': ['norway spruce'], 'latin': ['picea abies']},
     "Single stiff needles all around the twig; cones hang like ornaments; droopy tips."),
    ({'common': ['austrian pine', 'austrian black pine'], 'latin': ['pinus nigra']},
     "Needles in bundles of 2, long and very stiff — handle with care!"),
    ({'common': ['eastern hemlock'], 'latin': ['tsuga canadensis']},
     "Flat, short needles with white lines underneath, arranged in flat sprays; tiny cones."),
    ({'common': ['bald cypress'], 'latin': ['taxodium distichum']},
     "Soft, feathery needles in flat sprays — a deciduous conifer that drops in fall."),
    ({'common': ['english yew', 'yew'], 'latin': ['taxus baccata']},
     "Flat dark-green needles in flat sprays with two pale bands underneath — caution: toxic."),
    ({'common': ['sawara false cypress', 'false cypress'], 'latin': ['chamaecyparis pisifera']},
     "Scale-like foliage forming ferny flat sprays — often in colorful cultivars."),

    # Flowering / ornamental
    ({'common': ['crabapple'], 'latin': ['malus']},
     "Simple, oval, finely toothed leaves (sometimes slightly lobed) — classic crabapple."),
    ({'common': ['aristocrat pear', 'callery pear', 'pear'], 'latin': ['pyrus calleryana']},
     "Glossy oval leaves with fine teeth and wavy edges — showy white bloom in spring."),
    ({'common': ['hawthorn', 'winter king'], 'latin': ['crataegus viridis']},
     "Simple leaves with teeth, sometimes slightly lobed — look for persistent red berries."),
    ({'common': ['western catalpa', 'catalpa'], 'latin': ['catalpa speciosa']},
     "Huge heart-shaped leaves (to ~12\") — tropical look; long ‘cigar’ pods later."),

    # Other
    ({'common': ['honey locust'], 'latin': ['gleditsia triacanthos']},
     "Doubly compound leaves with many tiny oval leaflets — light, lacy shade."),
    ({'common': ['black locust'], 'latin': ['robinia pseudoacacia']},
        "Compound with 7–19 oval leaflets; paired thorns at the leaf bases."),
    ({'common': ['sweetgum', 'sweet gum'], 'latin': ['liquidambar styraciflua']},
     "Star-shaped leaves with 5–7 pointed lobes and fine teeth — aromatic when crushed."),
    ({'common': ['hackberry'], 'latin': ['celtis occidentalis']},
     "Elm-like oval leaf with toothed edges but an even base — unlike most elms."),
    ({'common': ['ohio buckeye'], 'latin': ['aesculus glabra']},
     "Palmately compound leaf with 5 leaflets radiating like a hand — shiny brown ‘buckeye’ nut later."),
    ({'common': ['yellow buckeye'], 'latin': ['aesculus flava']},
     "Palmately compound with 5–7 leaflets; yellow flower spikes distinguish it from Ohio buckeye."),
]


BARK_RULES: List[Tuple[Dict[str, List[str]], str]] = [
    ({'common': ['american sycamore', 'sycamore'], 'latin': ['platanus occidentalis']},
     "Spectacular camouflage — bark exfoliates in white, gray, tan, and green patches."),
    ({'common': ['london plane'], 'latin': ['platanus x acerifolia']},
     "Exfoliating bark in mottled patches, similar to sycamore."),
    ({'common': ['shagbark hickory'], 'latin': ['carya ovata']},
     "Long, shaggy strips peeling from the trunk — a tree in a fur coat!"),
    ({'common': ['river birch'], 'latin': ['betula nigra']},
     "Papery curls in cinnamon to salmon tones — beautiful peeling bark."),
    ({'common': ['yellow birch'], 'latin': ['betula alleghaniensis']},
     "Yellow-bronze bark peels in thin, papery curls; twigs can smell wintergreen when scraped."),
    ({'common': ['chestnut oak', 'basket oak'], 'latin': ['quercus montana', 'quercus prinus']},
     "Dark, deeply furrowed bark with thick ridges — like alligator skin."),
    ({'common': ['cherrybark oak'], 'latin': ['quercus pagoda']},
     "Dark bark with scaly ridges resembling black cherry — hence the name."),
    ({'common': ['chinese elm'], 'latin': ['ulmus parvifolia']},
     "Orange-gray-green bark exfoliates in puzzle-like flakes — striking even in winter."),
    ({'common': ['hackberry'], 'latin': ['celtis occidentalis']},
     "Warty, corky ridges create a distinctive, touchable pattern."),
    ({'common': ['american hornbeam', 'musclewood'], 'latin': ['carpinus caroliniana']},
     "Smooth, blue-gray bark with sinewy, muscle-like ridges."),
    ({'common': ['amur corktree', 'corktree'], 'latin': ['phellodendron amurense']},
     "Corky, deeply furrowed, spongy bark — soft to the touch."),
    ({'common': ['american beech'], 'latin': ['fagus grandifolia']},
     "Smooth, light gray ‘elephant skin’ bark (please don’t carve)."),
    ({'common': ['european beech'], 'latin': ['fagus sylvatica']},
     "Smooth silver-gray bark; many garden forms with elegant silhouettes."),
]


def _match(rules: List[Tuple[Dict[str, List[str]], str]], common: Optional[str], latin: Optional[str]) -> Optional[str]:
    c = _norm(common)
    l = _norm(latin)
    for (match, text) in rules:
        common_ok = any(token in c for token in match.get('common', [])) if c else False
        latin_ok = any(token in l for token in match.get('latin', [])) if l else False
        if common_ok or latin_ok:
            return text
    return None


def get_leaf_info(common_name: Optional[str], latin_name: Optional[str]) -> Optional[str]:
    return _match(LEAF_RULES, common_name, latin_name)


def get_bark_info(common_name: Optional[str], latin_name: Optional[str]) -> Optional[str]:
    return _match(BARK_RULES, common_name, latin_name)

