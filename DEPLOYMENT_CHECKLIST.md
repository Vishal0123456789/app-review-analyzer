# Deployment Checklist

## Pre-Deployment ✅

- [ ] All code committed to Git
- [ ] GitHub repository created
- [ ] Dockerfile created
- [ ] railway.json created
- [ ] vercel.json created
- [ ] DEPLOYMENT_GUIDE.md created

## GitHub Setup ✅

- [ ] GitHub account created
- [ ] Repository initialized: `app-review-analyzer`
- [ ] Code pushed to main branch
- [ ] Code visible on GitHub.com

## Railway Backend Deployment

### Setup
- [ ] Railway account created (https://railway.app)
- [ ] Project created in Railway
- [ ] GitHub repository connected
- [ ] Deployment successful (green status)

### Configuration
- [ ] GEMINI_API_KEY set
- [ ] DEFAULT_EMAIL set (agraharivishal19981@gmail.com)
- [ ] TO_EMAILS set
- [ ] SMTP_USERNAME set (your Gmail)
- [ ] SMTP_PASSWORD set (app password from Google)
- [ ] SMTP_HOST set (smtp.gmail.com)
- [ ] SMTP_PORT set (587)

### Verification
- [ ] Railway URL obtained
- [ ] Backend is running (check deployment status)
- [ ] Logs show no errors

## Gmail Configuration

- [ ] 2-Factor Authentication enabled
- [ ] App password generated
- [ ] App password stored securely

## Vercel Frontend Deployment

### Setup
- [ ] Vercel account created (https://vercel.com)
- [ ] GitHub repository connected to Vercel
- [ ] Build settings configured
- [ ] Environment variable VITE_API_URL set to Railway URL

### Build
- [ ] Build completed successfully
- [ ] No build errors in logs
- [ ] Vercel URL obtained

### Configuration
- [ ] VITE_API_URL matches Railway URL exactly

## Testing

### Backend Testing
- [ ] Can access Railway URL in browser
- [ ] HTTP 200 response from /docs endpoint
- [ ] Environment variables visible in logs

### Frontend Testing
- [ ] Can open Vercel URL in browser
- [ ] UI loads without errors
- [ ] Form inputs are visible
- [ ] Analysis button is clickable

### Integration Testing
- [ ] Frontend connects to Railway backend
- [ ] Form submission works
- [ ] Analysis completes
- [ ] Results display in frontend
- [ ] Download button works
- [ ] Email is sent

### Email Testing
- [ ] Test email received in inbox
- [ ] Subject line is correct
- [ ] Email body displays properly
- [ ] Includes correct date range

## Production Ready

- [ ] All tests passed
- [ ] No errors in logs
- [ ] Email delivery verified
- [ ] Frontend-backend communication working
- [ ] User can complete full workflow
- [ ] Documentation updated

## Post-Deployment

- [ ] Monitor logs for errors
- [ ] Set up email notifications (optional)
- [ ] Document Railway URL
- [ ] Document Vercel URL
- [ ] Share links with team
- [ ] Test weekly schedule (if configured)

## Troubleshooting Notes

Email issues:
- Verify Gmail app password (not regular password)
- Check 2-Factor Authentication is enabled
- Confirm SMTP credentials in Railway

Backend issues:
- Check Railway logs: `railway logs -f`
- Verify environment variables set
- Ensure Python requirements installed

Frontend issues:
- Check browser console (F12)
- Verify VITE_API_URL in Vercel settings
- Check Vercel build logs

Connection issues:
- Confirm Railway URL is correct
- Test URL directly in browser
- Check CORS settings

## Quick Links

- GitHub: https://github.com/YOUR_USERNAME/app-review-analyzer
- Railway: https://railway.app/project/YOUR_PROJECT_ID
- Vercel: https://vercel.com/YOUR_USERNAME/app-review-analyzer
- Gemini API Keys: https://aistudio.google.com/app/apikeys
- Gmail App Passwords: https://myaccount.google.com/apppasswords

---

## Contact & Support

For deployment issues:
1. Check DEPLOYMENT_GUIDE.md
2. Review Railway logs
3. Review Vercel logs
4. Check browser console (F12)

Good luck with your deployment! 🚀
