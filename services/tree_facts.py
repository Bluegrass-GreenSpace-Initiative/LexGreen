from __future__ import annotations

from typing import Optional


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


FACT_RULES = [
    # Deciduous Hardwoods - Large Shade Trees
    ({'common': ['red oak'], 'latin': ['quercus rubra']},
     'A single, mature red oak can produce over 700 acorns in a year, and their wood is commonly used for flooring and furniture.'),
    ({'common': ['willow oak'], 'latin': ['quercus phellos']},
     "Unlike other oaks, its leaves are narrow and lance-shaped, resembling a willow tree's leaves."),
    ({'common': ['sugar maple'], 'latin': ['acer saccharum']},
     'The sap of this tree is what is boiled down to create delicious maple syrup.'),
    ({'common': ['sawleaf zelkova', 'zelkova'], 'latin': ['zelkova serrata']},
     'This tree is highly resistant to Dutch Elm Disease and is often used as a replacement for the American Elm in landscaping.'),
    ({'common': ['bur oak'], 'latin': ['quercus macrocarpa']},
     'This species has the largest acorns of all native North American oaks, with caps that look like fuzzy fringes.'),
    ({'common': ['red maple'], 'latin': ['acer rubrum']},
     'The red maple is named for its red twigs, buds, flowers, and even seeds, which provide color in all four seasons.'),
    ({'common': ['pin oak'], 'latin': ['quercus palustris']},
     'The lower branches of a pin oak often point downwards, which is a key way to identify them.'),
    ({'common': ['white ash'], 'latin': ['fraxinus americana']},
     'Its wood is famous for being incredibly strong and flexible, making it the preferred material for baseball bats and tool handles.'),
    ({'common': ['shumard oak'], 'latin': ['quercus shumardii']},
     'This tree is known for its tolerance of heat and drought, making it a great choice for urban areas.'),

    # Evergreen Conifers
    ({'common': ['norway spruce'], 'latin': ['picea abies']},
     "This species is the world's fastest-growing spruce and is a common choice for Christmas trees."),
    ({'common': ['white pine'], 'latin': ['pinus strobus']},
        'The needles of this tree grow in clusters of five, which you can remember with the phrase "W-H-I-T-E" for each needle.'),
    ({'common': ['eastern hemlock'], 'latin': ['tsuga canadensis']},
     'This tree is unique among conifers for its flat, feathery sprays of needles and tiny cones.'),
    ({'common': ['english yew'], 'latin': ['taxus baccata']},
     'All parts of this tree, except the red berries, are poisonous to humans and animals.'),

    # Deciduous Hardwoods - Flowering Trees
    ({'common': ['aristocrat pear'], 'latin': ['pyrus calleryana']},
     'This tree is a popular ornamental because of its showy white flowers in the spring and glossy purple leaves in the fall.'),
    ({'common': ['southern magnolia'], 'latin': ['magnolia grandiflora']},
     'It\'s famous for its huge, fragrant white flowers and glossy leaves that remain on the tree year-round.'),
    ({'common': ['eastern redbud'], 'latin': ['cercis canadensis']},
     'Its flowers bloom directly from the branches and trunk, a trait known as cauliflory.'),
    ({'common': ['crabapple'], 'latin': ['malus']},
     'The fruit of this tree, while small and often bitter, is an important food source for birds and other wildlife throughout the winter.'),
    ({'common': ['goldenrain tree','golden rain'], 'latin': ['koelreuteria paniculata']},
     'It gets its name from its beautiful sprays of yellow flowers that resemble golden rain in the summer.'),
    ({'common': ['winter king hawthorn','hawthorn'], 'latin': ['crataegus viridis']},
     'This tree is valued for its long-lasting, bright red berries that stay on the branches all winter, providing food for birds.'),

    # Deciduous Hardwoods - Nut Trees
    ({'common': ['black walnut'], 'latin': ['juglans nigra']},
     'The roots of this tree release a substance called juglone, which is toxic to many other plants, preventing them from growing nearby.'),
    ({'common': ['shagbark hickory'], 'latin': ['carya ovata']},
     'The bark of this tree peels off in long strips, giving it a distinctive shaggy appearance.'),

    # Other/Unique
    ({'common': ['ginkgo','maidenhair'], 'latin': ['ginkgo biloba']},
     'It is considered a "living fossil" because it is the only remaining species of a very old plant family. The female trees produce a fruit that has a very strong, unpleasant smell.'),
]


def get_tree_fact(common_name: Optional[str], latin_name: Optional[str]) -> Optional[str]:
    c = _norm(common_name)
    l = _norm(latin_name)
    for (match, fact) in FACT_RULES:
        common_ok = any(token in c for token in match.get('common', [])) if c else False
        latin_ok = any(token in l for token in match.get('latin', [])) if l else False
        if common_ok or latin_ok:
            return fact
    return None

