from __future__ import annotations
from random import randint
from typing import Optional


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


FACT_RULES = [
    # Deciduous Hardwoods - Large Shade Trees
    ({'common': ['red oak'], 'latin': ['quercus rubra']},
     ['A single, mature red oak can produce over 700 acorns in a year, and their wood is commonly used for flooring and furniture.', 'Red oaks can often grow to be around 70 to 80 feet tall with trunks 2-3 feet in diameter.', 'The acorns of this tree are an important source of food for several animals such as deer, squirrels, and turkeys.']),
    ({'common': ['willow oak'], 'latin': ['quercus phellos']},
     ["Unlike other oaks, its leaves are narrow and lance-shaped, resembling a willow tree's leaves.", 'The leaves of this tree can turn shades of yellow, orange, and red in the fall.', 'The willow oak is a valued ornamental tree due to the shade it provides and its realitively quick growth.']),
    ({'common': ['sugar maple'], 'latin': ['acer saccharum']},
     ['The sap of this tree is what is boiled down to create delicious maple syrup.', 'Forests of sugar maples have dense shade and almost no understory.', 'The leaf of this tree is featured on Canada\'s national flag.']),
    ({'common': ['sawleaf zelkova', 'zelkova'], 'latin': ['zelkova serrata']},
     ['This tree is highly resistant to Dutch Elm Disease and is often used as a replacement for the American Elm in landscaping.', 'The leaves of this tree have a rough texture on the top, but a smooth texture on the bottom.', 'This tree is commonly used for bonzai.']),
    ({'common': ['bur oak'], 'latin': ['quercus macrocarpa']},
     ['This species has the largest acorns of all native North American oaks, with caps that look like fuzzy fringes.', 'The bur oak\'s lumber is similar to strength and durability as lumber from white oaks.', 'The natural range of this tree is the furthest west and north of all eastern oaks.']),
    ({'common': ['red maple'], 'latin': ['acer rubrum']},
     ['The red maple is named for its red twigs, buds, flowers, and even seeds, which provide color in all four seasons.', 'This tree\'s distribution ranges from Canada in the north to Florida and Texas in the south.', 'The roots of this tree often prevent other plants from growing near its trunk.']),
    ({'common': ['pin oak'], 'latin': ['quercus palustris']},
     ['The lower branches of a pin oak often point downwards, which is a key way to identify them.', 'This tree grows both male and female flowers on the same tree making it monoecious.', 'In the wild the top branches of this tree often block light from the lower branches, causing them to break and leave pin-like stubs.']),
    ({'common': ['white ash'], 'latin': ['fraxinus americana']},
     ['Its wood is famous for being incredibly strong and flexible, making it the preferred material for baseball bats and tool handles.', 'White oaks commonly form trunk cavaties which create homes for animals like woodpeckers and owls.', 'The seedlings of this tree are able to penetrate through thickets of invasive species and reach the forest canopy.']),
    ({'common': ['shumard oak'], 'latin': ['quercus shumardii']},
     ['This tree is known for its tolerance of heat and drought, making it a great choice for urban areas.', 'This tree is named after Benjamin Franklin Shumard, a geoligist who organized the first geological survey of Texas.', 'The acorns of this tree mature every two years.']),

    # Evergreen Conifers
    ({'common': ['norway spruce'], 'latin': ['picea abies']},
     ["This species is the world's fastest-growing spruce and is a common choice for Christmas trees.", 'This tree is native to North and Central Europe.', 'Normally this tree grows to around 100-150 feet tall, however it often only grows to around 40-60 feet tall in North America.']),
    ({'common': ['white pine'], 'latin': ['pinus strobus']},
     ['The needles of this tree grow in clusters of five, which you can remember with the phrase "W-H-I-T-E" for each needle.', 'In colonial times this tree was often reserved by the British crown for use as ship masts.', 'This tree is the state tree of Maine, with the pine cone and tassel being used in the state\'s emblem.']),
    ({'common': ['eastern hemlock'], 'latin': ['tsuga canadensis']},
     ['This tree is unique among conifers for its flat, feathery sprays of needles and tiny cones.', 'The top of this tree often droops rather than having pointed top like most other pine trees.', 'This tree is sometimes nicknamed the \"redwood of the east\" since it can live over 500 years and grow up to over 170 feet.']),
    ({'common': ['english yew'], 'latin': ['taxus baccata']},
     ['All parts of this tree are poisonous to humans and animals.', 'Ancient Greeks wove funeral wreaths from this tree to honor Hecate.', 'The wood of this tree was frequently used in the longbows of English archers.']),

    # Deciduous Hardwoods - Flowering Trees
    ({'common': ['aristocrat pear'], 'latin': ['pyrus calleryana']},
     ['This tree is a popular ornamental because of its showy white flowers in the spring and glossy purple leaves in the fall.', 'This tree is susceptible to having braches break in strong winds.', 'In the 1950s this tree was a highly valued landscaping tree.']),
    ({'common': ['southern magnolia'], 'latin': ['magnolia grandiflora']},
     ['It\'s famous for its huge, fragrant white flowers and glossy leaves that remain on the tree year-round.', 'Magnolia\'s are one of the oldest flowering plant genus, going back to around 130 million years.', 'This tree is the state tree of Mississippi.']),
    ({'common': ['eastern redbud'], 'latin': ['cercis canadensis']},
     ['Its flowers bloom directly from the branches and trunk, a trait known as cauliflory.', 'This tree belongs to the Leguminosae, or Legume, family of plants.', 'The seeds of this tree are created inside bean-like pods that can remain on the tree into winter.']),
    ({'common': ['crabapple'], 'latin': ['malus']},
     ['The fruit of this tree, while small and often bitter, is an important food source for birds and other wildlife throughout the winter.', 'This tree can have a bloom period of up to four weeks depending on the weather.', 'The color of blossoms of this tree can range wildly from white to a dark, purplish red.']),
    ({'common': ['goldenrain tree','golden rain'], 'latin': ['koelreuteria paniculata']},
     ['It gets its name from its beautiful sprays of yellow flowers that resemble golden rain in the summer.', 'This tree has a short germination time of a few days, allowing it to spread quickly and shade out native species.', 'This tree was originally introduced to the US as an ornamental tree from Asia.']),
    ({'common': ['winter king hawthorn','hawthorn'], 'latin': ['crataegus viridis']},
     ['This tree is valued for its long-lasting, bright red berries that stay on the branches all winter, providing food for birds.', 'Hawthorn trees have connection to fairies in Celtic folklore.', 'This tree often grows thorns of around 1-3 inches in length.']),

    # Deciduous Hardwoods - Nut Trees
    ({'common': ['black walnut'], 'latin': ['juglans nigra']},
     ['The roots of this tree release a substance called juglone, which is toxic to many other plants, preventing them from growing nearby.', 'The wood of this tree is highly prized for use in furniture, gunstocks, and vaneer.', 'This tree grows nuts that when broken have an edible inside.']),
    ({'common': ['shagbark hickory'], 'latin': ['carya ovata']},
     ['The bark of this tree peels off in long strips, giving it a distinctive shaggy appearance.', 'This tree is used commercially to produce hickory nuts.', 'The nuts of this tree are encased in a thick husk that split when it ripe in the fall.']),

    # Other/Unique
    ({'common': ['ginkgo','maidenhair'], 'latin': ['ginkgo biloba']},
     ['It is considered a "living fossil" because it is the only remaining species of a very old plant family. The female trees produce a fruit that has a very strong, unpleasant smell.', 'This tree has bright green fan-shaped leaves that turn bright yellow and orange in the fall.', 'In the fall the leaves of this tree often fall off all at once, creating a carpet near its base.']),
]


def get_tree_fact(common_name: Optional[str], latin_name: Optional[str]) -> Optional[str]:
    c = _norm(common_name)
    l = _norm(latin_name)
    for (match, fact) in FACT_RULES:
        common_ok = any(token in c for token in match.get('common', [])) if c else False
        latin_ok = any(token in l for token in match.get('latin', [])) if l else False
        if common_ok or latin_ok:
            return fact[randint(0,2)]
    return None

