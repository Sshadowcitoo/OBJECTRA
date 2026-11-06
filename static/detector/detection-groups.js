function groupDetections(detections) {
  const groups = new Map();
  for (const detection of detections) {
    if (!groups.has(detection.class_id)) {
      groups.set(detection.class_id, { classId: detection.class_id, name: detection.name, items: [] });
    }
    groups.get(detection.class_id).items.push(detection);
  }
  return [...groups.values()].map(group => {
    const items = [...group.items].sort((a, b) => b.confidence - a.confidence);
    return {
      ...group,
      items,
      confidence: items.reduce((sum, item) => sum + item.confidence, 0) / items.length
    };
  }).sort((a, b) => b.items.length - a.items.length || b.confidence - a.confidence);
}

if (typeof module !== 'undefined') module.exports = { groupDetections };