// Shared tree icon helper for consistent marker and inline icons
// Provides two helpers:
//  - window.treeIcons.getIconUrl(latinName, commonName)
//  - window.treeIcons.getLeafletIcon(latinName, commonName)

(function(){
  const base = '/static/images/tree-markers';

  function getIconName(latin = '', common = '') {
    const s = String(latin || '').toLowerCase();
    const c = String(common || '').toLowerCase();

    if (s.includes('stump') || c.includes('stump')) return 'stump';
    if (s.includes('quercus') || c.includes('oak')) return 'oak';
    if (s.includes('acer') || c.includes('maple')) return 'maple';
    if (s.includes('ginkgo') || s.includes('gingko') || c.includes('ginkgo') || c.includes('gingko')) return 'gingko';
    if (s.includes('juglans') || c.includes('walnut')) return 'walnut';
    if (s.includes('ulmus') || c.includes('elm')) return 'elm';
    if (s.includes('carya') || c.includes('hickory') || c.includes('pecan')) return 'hickory';

    const evergreenGenera = ['pinus','picea','abies','juniperus','thuja','cupressus','chamaecyparis','cedrus','taxus','ilex','tsuga','pseudotsuga'];
    const evergreenNames = ['pine','spruce','fir','juniper','cedar','cypress','yew','hemlock','holly','evergreen'];
    if (evergreenGenera.some(g => s.includes(g)) || evergreenNames.some(n => c.includes(n))) return 'evergreen';

    const floweringGenera = ['prunus','malus','magnolia','cercis','cornus','amelanchier','lagerstroemia','styrax','crataegus','pyrus','liriodendron','tilia','catalpa','koelreuteria'];
    const floweringNames = ['cherry','apple','crabapple','magnolia','redbud','dogwood','serviceberry','hawthorn','pear','crape','tulip','flowering','catalpa','goldenrain','golden rain'];
    if (floweringGenera.some(g => s.includes(g)) || floweringNames.some(n => c.includes(n))) return 'flowering';

    const deciduousGenera = ['liquidambar','carya','ulmus','fraxinus','fagus','platanus','celtis','zelkova','aesculus','gleditsia','styphnolobium','sophora'];
    const deciduousNames = ['sweet gum','sweetgum','pecan','elm','hickory','ash','beech','sycamore','yellowwood','american yellowwood','yellow wood','hackberry','zelkova','sawleaf zelkova','buckeye','honey locust','locust','japanese pagoda','pagoda'];
    if (deciduousGenera.some(g => s.includes(g)) || deciduousNames.some(n => c.includes(n))) return 'deciduous';

    return 'deciduous';
  }

  function getIconUrl(latin, common) {
    const name = getIconName(latin, common);
    return `${base}/${name}.svg`;
  }

  function getLeafletIcon(latin, common) {
    if (typeof L === 'undefined' || !L || !L.icon) return null;
    return L.icon({ iconUrl: getIconUrl(latin, common), iconSize: [24,24], iconAnchor: [12,12] });
  }

  window.treeIcons = { getIconUrl, getLeafletIcon };
})();

