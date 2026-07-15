<script setup>
const treks = [
  {
    name: 'Kedarkantha',
    location: 'Uttarakhand',
    duration: '6 Days',
    price: '₹X,499',
    image: 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=600',
  },
  {
    name: 'Hampta Pass',
    location: 'Himachal Pradesh',
    duration: '5 Days',
    price: '₹XX,999',
    image: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600',
  },
  {
    name: 'Valley of Flowers',
    location: 'Uttarakhand',
    duration: '4 Days',
    price: '₹X,999',
    image: 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=600',
  },
]
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light border-bottom">
    <div class="container">
      <RouterLink to="/" class="navbar-brand">GoTrek</RouterLink>
      <div class="d-flex gap-2">
        <RouterLink to="/login" class="btn btn-outline-secondary btn-sm">Log in</RouterLink>
        <RouterLink to="/signup" class="btn btn-primary btn-sm">Sign up</RouterLink>
      </div>
    </div>
  </nav>

  <header class="container py-5">
    <div class="row align-items-center g-4">
      <div class="col-lg-6">
        <h1 class="display-6 fw-bold">Book guided treks across India</h1>
        <p class="text-muted mt-3">
          GoTrek lists guided treks across the Himalayas and Western Ghats. Browse routes,
          check available slots, and book directly — no phone calls required.
        </p>
        <RouterLink to="/signup" class="btn btn-primary mt-2">Get started</RouterLink>
      </div>
      <div class="col-lg-6">
        <img src="https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800" class="img-fluid rounded" alt="Mountain trek" />
      </div>
    </div>
  </header>

  <section class="container py-4">
    <div class="row row-cols-1 row-cols-md-3 g-4 text-center">
      <div class="col">
        <h3 class="h6">Certified guides</h3>
        <p class="text-muted small">Every trek is led by a locally certified guide.</p>
      </div>
      <div class="col">
        <h3 class="h6">Real-time slots</h3>
        <p class="text-muted small">Booking checks live availability before confirming.</p>
      </div>
      <div class="col">
        <h3 class="h6">Track your bookings</h3>
        <p class="text-muted small">See booking and payment status from your dashboard.</p>
      </div>
    </div>
  </section>

  <section class="container py-4">
    <h2 class="h4 mb-3">Featured Treks</h2>
    <div class="row row-cols-1 row-cols-md-3 g-3">
      <div v-for="trek in treks" :key="trek.name" class="col">
        <div class="card h-100">
          <img :src="trek.image" class="card-img-top" :alt="trek.name" style="height: 180px; object-fit: cover" />
          <div class="card-body">
            <h3 class="h6">{{ trek.name }}</h3>
            <p class="text-muted small mb-2">{{ trek.location }}</p>
            <div class="d-flex justify-content-between small mb-2">
              <span>{{ trek.duration }}</span>
              <strong>{{ trek.price }}</strong>
            </div>
            <RouterLink to="/signup" class="btn btn-outline-primary btn-sm w-100">View details</RouterLink>
          </div>
        </div>
      </div>
    </div>
  </section>

  <footer class="border-top py-3 mt-4 text-center text-muted small">
    &copy; 2026 GoTrek
  </footer>
</template>
