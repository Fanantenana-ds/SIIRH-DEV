import React from "react";

export default function DisciplineTable({ cases, onView, onConvocation, onDecision }) {
  return (
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>Employé</th>
          <th>Type de faute</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        {cases.map((c) => (
          <tr key={c.id}>
            <td>{c.id}</td>
            <td>{c.employee_name}</td>
            <td>{c.fault_type}</td>
            <td>{c.status}</td>
            <td>
              <button onClick={() => onView(c)}>Voir</button>
              <button onClick={() => onConvocation(c)}>Convocation</button>
              <button onClick={() => onDecision(c)}>Décision</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
