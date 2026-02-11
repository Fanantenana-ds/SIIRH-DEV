// // // src/components/StarRating.jsx
// // import React, { useState } from "react";
// // import { Star } from "lucide-react";

// // const StarRating = ({ value, onChange }) => {
// //   const [hover, setHover] = useState(null);

// //   return (
// //     <div style={{ display: "flex", gap: "6px" }}>
// //       {[1, 2, 3, 4, 5].map((star) => (
// //         <Star
// //           key={star}
// //           size={22}
// //           onClick={() => onChange(star)}
// //           onMouseEnter={() => setHover(star)}
// //           onMouseLeave={() => setHover(null)}
// //           style={{
// //             cursor: "pointer",
// //             color:
// //               star <= (hover || value)
// //                 ? "#facc15" // Jaune (étoile active)
// //                 : "#d1d5db", // Gris (étoile inactive)
// //             transition: "color 0.2s ease",
// //           }}
// //         />
// //       ))}
// //     </div>
// //   );
// // };

// // export default StarRating;


// import React from "react";
// import { FaStar } from "react-icons/fa";

// export default function StarRating({ value, onChange }) {
//   return (
//     <div className="star-rating">
//       {[1, 2, 3, 4, 5].map((star) => (
//         <FaStar
//           key={star}
//           size={22}
//           color={star <= value ? "#f5b301" : "#ccc"}
//           onClick={() => onChange(star)}
//           style={{ cursor: "pointer", marginRight: 4 }}
//         />
//       ))}
//     </div>
//   );
// }





import React, { useState } from "react";
import { FaStar } from "react-icons/fa";

export default function StarRating({ value, onChange }) {
  const [hover, setHover] = useState(null);

  return (
    <div className="flex gap-1 items-center">
      {[1, 2, 3, 4, 5].map((star) => (
        <FaStar
          key={star}
          size={22}
          color={star <= (hover || value) ? "#f5b301" : "#ccc"}
          onClick={() => onChange(star)}
          onMouseEnter={() => setHover(star)}
          onMouseLeave={() => setHover(null)}
          style={{ cursor: "pointer" }}
        />
      ))}
    </div>
  );
}
