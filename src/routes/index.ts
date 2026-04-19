import { Hono } from 'hono'
import { adminRoutes } from './admin'
import { bookingRoutes } from './booking'
import { internalRoutes } from './internal'
import { usersRoutes } from './users'

export const routes = new Hono()

routes.route('/', bookingRoutes)
routes.route('/users', usersRoutes)
routes.route('/admin', adminRoutes)
routes.route('/internal', internalRoutes)
