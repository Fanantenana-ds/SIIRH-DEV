export default function CardStat({ title, value, color }) {
  const colors = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    orange: "bg-orange-500",
  };

  return (
    <div className={`p-6 rounded-xl text-white shadow ${colors[color]}`}>
      <h3 className="text-sm uppercase font-semibold">{title}</h3>
      <p className="text-3xl font-bold mt-2">{value}</p>
    </div>
  );
}
