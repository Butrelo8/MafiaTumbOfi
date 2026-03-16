import { Hono } from 'hono'
import { authRoutes } from './auth'
import { bookingRoutes } from './booking'
import { usersRoutes } from './users'
import { adminRoutes } from './admin'

export const routes = new Hono()

routes.route('/auth', authRoutes)
routes.route('/', bookingRoutes)
routes.route('/users', usersRoutes)
routes.route('/admin', adminRoutes)
