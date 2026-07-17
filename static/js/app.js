import { setupTheme } from "./core/theme.js";
import { markActiveNavigation } from "./core/active-navigation.js";
import { setupMobileMenu } from "./core/mobile-menu.js";
import { setupDesktopDropdowns } from "./components/desktop-dropdowns.js";
import { setupTagCloudDialog } from "./components/tag-cloud.js";
import { setupPostDetail } from "./pages/post-detail.js";
import {
    setupReadingNavigator,
} from "./components/reading-navigator.js";
import {
    setupSignatureAnimation,
} from "./components/signature.js";
import {
    setupNoteDetail,
} from "./pages/note-detail.js";
import {
    setupTimelinePage,
} from "./pages/timeline.js";

document.addEventListener("DOMContentLoaded", () => {
    setupTheme();
    markActiveNavigation();
    setupMobileMenu();
    setupDesktopDropdowns();
    setupTagCloudDialog();
    setupPostDetail();
    setupReadingNavigator();
    setupSignatureAnimation();
    setupNoteDetail();
    setupTimelinePage();
});
